import json
import logging

import httpx
from bs4 import BeautifulSoup
from faker.proxy import Faker
from googlesearch import search
from openai import OpenAI
from tenacity import stop_after_attempt, retry

from app.config import settings
from app.schemas.request import AgentResponse, PredictionRequest, PredictionResponse


logger = logging.getLogger("uvicorn")

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

class WebQueryService:

    def __init__(self):
        self._faker_tool = Faker()



        self._ai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_ENDPOINT)
        self._model_version = settings.OPENAI_MODEL_NAME
        self._base_prompt = settings.SYSTEM_INSTRUCTION

    async def process_query(self, request: PredictionRequest) -> PredictionResponse:
        query_content = request.query
        parts = query_content.split('\n1.', 1)
        question, options = parts if len(parts) == 2 else (query_content, '')
        logger.debug(f'Received Query: {query_content}, Parsed question: {question}, Options: {options}')

        search_results = await self.retrieve_links(question, max_links=1)
        logger.debug(f'Obtained Links: {search_results}')

        gathered_context = await self._fetch_web_content(search_results)

        refined_prompt = await self._construct_prompt(question, options, gathered_context)
        response = await self.generate_response(refined_prompt)
        logger.debug(f'Generated Response: {response}')

        final_result = PredictionResponse(
            id=request.id,
            answer=None if options == "" else response.answer,
            reasoning=response.reasoning + self.signature(),
            sources=search_results
        )
        logger.debug(f'Finalized Response: {final_result}')
        return final_result

    async def _construct_prompt(self, inquiry: str, options: str, context: str) -> str:
        return f'''
        Ответь на данный вопрос: {inquiry}\n
        Выбери правильный вариант ответа:
        {options}\n
        Ответ необходимо оформить в строгом формате:
        {{ "answer": номер правильного варианта, "reasoning": объяснение выбора, "sources": [список использованных источников] }}
        Если вариантов ответа нет, в поле ответа укажи null.

        Используй следующие сведения, собранные из веб-источников:
        {context}
        '''

    @retry(stop=stop_after_attempt(3))
    async def _download_page_content(self, url):
        headers = {"User-Agent": self._faker_tool.user_agent()}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            parsed_content = BeautifulSoup(response.text, "html.parser").get_text(separator="\n", strip=True)
            return parsed_content

    async def _fetch_web_content(self, urls: list[str]) -> str:
        combined_content = ""
        for url in urls:
            try:
                combined_content += await self._download_page_content(url) + '\n\n'
            except Exception as err:
                logger.error(f'Failed to retrieve {url}: {err}')

        return combined_content

    async def retrieve_links(self, query_text: str, max_links: int = 3) -> list[str]:
        """
        Получить список релевантных ссылок на основе поискового запроса
        :param query_text: Исходный текст запроса
        :param max_links: Максимальное количество ссылок
        :return: Список URL
        """
        refined_query = self._extract_main_query(query_text)
        return [link for link in search(refined_query, num_results=max_links)]

    def _extract_main_query(self, full_text: str) -> str:
        """
        Извлечь основную часть запроса, исключив варианты ответов
        :param full_text: Полный запрос
        :return: Отфильтрованный запрос
        """
        return full_text.split("\n1.", 1)[0]

    @retry(reraise=True, stop=stop_after_attempt(3))
    async def generate_response(self, prompt_text: str) -> AgentResponse:
        response = self._ai_client.chat.completions.create(
            model=self._model_version,
            messages=[
                {"role": "system", "content": self._base_prompt},
                {"role": "user", "content": prompt_text},
            ]
        )

        logger.debug(f"Response from GPT: {response}")
        formatted_response = response.choices[0].message.content.replace("```json", '').replace("```", '')
        logger.debug(f"Parsed JSON Response: {formatted_response}")
        response_data = json.loads(formatted_response)

        return AgentResponse(**response_data)

    def signature(self):
        return f"\n{self._model_version}"
