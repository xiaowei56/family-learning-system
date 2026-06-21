"""
LLM API 服务层

封装对本地 LLM API（兼容 OpenAI 格式）的调用，提供 AI 评估、解题生成等功能。
"""

import json
from typing import Optional

import httpx

from app.config import settings

# ─── 默认系统提示词 ───────────────────────────────────

SYSTEM_PROMPT_EVALUATE = """你是一位专业的 K12 学科教师。请评估学生的作答是否正确，并给出详细分析。
要求：
1. 判断答案对错，给出明确结论
2. 如果错误，分析错误原因（概念理解偏差/计算失误/审题不清等）
3. 给出正确答案
4. 语气专业且有耐心"""

SYSTEM_PROMPT_SOLUTION = """你是一位专业的 K12 学科教师。请给出详细的解题过程。
要求：
1. 分步骤展示解题思路
2. 解释每一步的原理和依据
3. 指出易错点
4. 如果涉及公式，用 LaTeX 格式（$$...$$）标注
5. 语言简洁明了，适合学生理解"""

SYSTEM_PROMPT_SIMILAR = """你是一位专业的 K12 学科出题教师。请生成一道与给定题目类似的练习题。
要求：
1. 考察相同的知识点
2. 难度相当或略高
3. 题型相似
4. 提供完整解题过程和答案
5. 用 LaTeX 格式标注公式"""

SYSTEM_PROMPT_WEAK_POINT = """你是一位专业的 K12 学习诊断分析师。基于学生的错题记录和考试成绩，进行薄弱点分析。
要求：
1. 识别知识点掌握程度的强弱
2. 按掌握程度对知识点排序（从弱到强）
3. 给出针对性的学习建议
4. 建议具体可行的提升方法"""


class LLMService:
    """LLM API 服务封装"""

    def __init__(self) -> None:
        self.api_url = settings.llm_api_url.rstrip("/")
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model

    async def _call(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Optional[str]:
        """调用 LLM API 的通用方法。"""
        url = f"{self.api_url}/chat/completions"

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException:
            return None
        except Exception as e:
            print(f"LLM API 调用失败: {e}")
            return None

    async def evaluate_answer(
        self, problem_text: str, student_answer: str, subject: str
    ) -> Optional[dict]:
        """评估学生作答是否正确。"""
        user_message = (
            f"科目：{subject}\n"
            f"题目：{problem_text}\n"
            f"学生作答：{student_answer}\n\n"
            "请按以下 JSON 格式回复（不要包含其他内容）：\n"
            '{"is_correct": true/false, "evaluation": "分析原因", "correct_answer": "正确答案"}'
        )

        result = await self._call(SYSTEM_PROMPT_EVALUATE, user_message, temperature=0.3)
        if not result:
            return None

        try:
            # 尝试从返回内容中提取 JSON
            result_clean = result.strip()
            if result_clean.startswith("```"):
                result_clean = result_clean.split("\n", 1)[-1]
                result_clean = result_clean.rsplit("```", 1)[0]
            return json.loads(result_clean)
        except json.JSONDecodeError:
            # 非 JSON 返回时，尝试简单解析
            return {
                "is_correct": "正确" in result[:50],
                "evaluation": result,
                "correct_answer": None,
            }

    async def generate_solution(
        self, problem_text: str, subject: str, knowledge_point: str
    ) -> Optional[dict]:
        """生成解题过程。"""
        user_message = (
            f"科目：{subject}\n"
            f"知识点：{knowledge_point}\n"
            f"题目：{problem_text}\n\n"
            "请按以下 JSON 格式回复（不要包含其他内容）：\n"
            '{"solution": "详细的解题步骤", "approach": "解题思路分析"}'
        )

        result = await self._call(SYSTEM_PROMPT_SOLUTION, user_message, temperature=0.5)
        if not result:
            return None

        try:
            result_clean = result.strip()
            if result_clean.startswith("```"):
                result_clean = result_clean.split("\n", 1)[-1]
                result_clean = result_clean.rsplit("```", 1)[0]
            return json.loads(result_clean)
        except json.JSONDecodeError:
            return {"solution": result, "approach": "请参考以上解题步骤"}

    async def generate_similar_problem(
        self, problem_text: str, subject: str, knowledge_point: str
    ) -> Optional[dict]:
        """生成相似练习题。"""
        user_message = (
            f"科目：{subject}\n"
            f"知识点：{knowledge_point}\n"
            f"原题：{problem_text}\n\n"
            "请按以下 JSON 格式回复（不要包含其他内容）：\n"
            '{"problem": "相似题目", "answer": "答案", "solution": "解题过程", "difficulty": 1}'
        )

        result = await self._call(SYSTEM_PROMPT_SIMILAR, user_message, temperature=0.8)
        if not result:
            return None

        try:
            result_clean = result.strip()
            if result_clean.startswith("```"):
                result_clean = result_clean.split("\n", 1)[-1]
                result_clean = result_clean.rsplit("```", 1)[0]
            return json.loads(result_clean)
        except json.JSONDecodeError:
            return {"problem": result, "answer": "", "solution": "", "difficulty": 1}

    async def analyze_weak_points(
        self, wrong_problems: list[dict], exam_scores: list[dict]
    ) -> Optional[dict]:
        """分析薄弱知识点。"""
        user_message = (
            "以下是学生的错题记录和考试成绩：\n\n"
            f"错题记录：{json.dumps(wrong_problems, ensure_ascii=False)}\n\n"
            f"考试成绩：{json.dumps(exam_scores, ensure_ascii=False)}\n\n"
            "请按以下 JSON 格式回复（不要包含其他内容）：\n"
            '{"weak_points": [{"subject": "数学", "knowledge_point": "一元二次方程", '
            '"mastery_level": 0.3, "suggestion": "学习建议"}], '
            '"overall_diagnosis": "总体诊断", "study_plan": "学习计划"}'
        )

        result = await self._call(SYSTEM_PROMPT_WEAK_POINT, user_message, temperature=0.5)
        if not result:
            return None

        try:
            result_clean = result.strip()
            if result_clean.startswith("```"):
                result_clean = result_clean.split("\n", 1)[-1]
                result_clean = result_clean.rsplit("```", 1)[0]
            return json.loads(result_clean)
        except json.JSONDecodeError:
            return {
                "weak_points": [],
                "overall_diagnosis": result,
                "study_plan": "",
            }

    async def generate_practice_paper(
        self, weak_points: list[dict], subject: str, question_count: int = 10
    ) -> Optional[list[dict]]:
        """根据薄弱点生成练习试卷。"""
        points_desc = ", ".join([p.get("knowledge_point", "") for p in weak_points])
        user_message = (
            f"科目：{subject}\n"
            f"薄弱知识点：{points_desc}\n"
            f"题目数量：{question_count}\n\n"
            "请生成一份针对性练习试卷，按以下 JSON 格式回复（不要包含其他内容）：\n"
            '[{"problem": "题目", "answer": "答案", "solution": "解题过程", '
            '"knowledge_point": "知识点", "difficulty": 1}, ...]'
        )

        result = await self._call(SYSTEM_PROMPT_SIMILAR, user_message, temperature=0.7)
        if not result:
            return None

        try:
            result_clean = result.strip()
            if result_clean.startswith("```"):
                result_clean = result_clean.split("\n", 1)[-1]
                result_clean = result_clean.rsplit("```", 1)[0]
            return json.loads(result_clean)
        except json.JSONDecodeError:
            return []


llm_service = LLMService()
