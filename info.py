import json
import time
from abc import ABC, abstractmethod
import requests


class GetAPI(ABC):
    @abstractmethod
    def request_api(self, keyword):
        pass


class HH(GetAPI):
    """Класс для работы с АPI сайто hh.ru"""
    def __init__(self, url):
        self.url = url

    def get_formatted_vacancies(self, keyword):
        """Функция не сохраняет вакансии без указания зарплаты и создает экземпляр класса Vacancy"""
        all_hh_vacancies = self.request_api(keyword)
        for vacancy in all_hh_vacancies:
            if vacancy["salary"]:
                if vacancy["salary"]["from"] and vacancy["salary"]["to"]:
                    Vacancy(vacancy["area"]["name"], vacancy["salary"]["from"], vacancy["salary"]["to"],
                            vacancy["snippet"]["requirement"], vacancy["name"], vacancy["id"],
                            "https://hh.ru/vacancy/" + vacancy["id"])

    def request_api(self, keyword):
        """Получает JSON файл с вакансиями по AIP с сайта hh.ru"""
        all_hh_vacancies = []
        for page in range(10):
            time.sleep(1)
            params = {
                "text": keyword,
                "page": page,
                "per_page": "100"
            }

            all_hh_vacancies.extend(requests.get(self.url, params=params).json()["items"])
        return all_hh_vacancies


class SJ(GetAPI):
    """Класс для работы с сайтом superjob.ru"""
    def __init__(self, url, header):
        self.url = url
        self.header = header

    def get_formatted_vacancies(self, keyword):
        """Создает экземпляр класса Vacancy"""
        all_sj_vacancies = self.request_api(keyword)
        for vacancy in all_sj_vacancies:
            Vacancy(vacancy["town"]["title"], vacancy["payment_from"], vacancy["payment_to"],
                    vacancy["candidat"],
                    vacancy["profession"], vacancy["id"], vacancy["link"])

    def request_api(self, keyword):
        """Получает JSON файл с вакансиями по API с сайта superjob.ru и удаляет дубликаты"""
        all_sj_vacancies = []
        for page in range(6):
            headers = {"X-Api-App-Id": self.header}
            params = {
                "count": 100,
                "keyword": keyword,
                "page": page,
                "archive": False
            }
            all_sj_vacancies.extend(requests.get(self.url, params=params, headers=headers).json()["objects"])
        vacancy_id = [vacancy["id"] for vacancy in all_sj_vacancies]
        for vacancy in all_sj_vacancies:
            if vacancy["id"] in vacancy_id:
                all_sj_vacancies.remove(vacancy)
        return all_sj_vacancies


class Vacancy:
    """Работает с сохраненными вакансиями , сравнивает, сортирует и фильтрует"""
    all_vacancies = []

    def __init__(self, area, salary_from, salary_to, requirement, professional_name, id, url):
        """area --  регион работодателя
           salary_from -- зарплата от
           salary_to -- зарплата до
           requirement -- обязанности и требования
           professional_name -- название профессии
           id  --  ID вакансии
           url  -- ссылка на вакансию"""
        self.area = area
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.requirement = requirement
        self.professional_name = professional_name
        self.id = id
        self.url = url
        Vacancy.all_vacancies.append(self)

    def __lt__(self, other):
        return self.salary_from < other.salary_from

    def __str__(self):
        return f"""Вакансия {self.professional_name},
        зарплата от {self.salary_from} до {self.salary_to}, 
        местоположение  {self.area}, ссылка на вакансию {self.url}, ID : {self.id}
        """

    @classmethod
    def sort_vacancies(cls):
        Vacancy.all_vacancies = sorted(Vacancy.all_vacancies, reverse=True)

    @classmethod
    def filtered_area(cls, key_area):
        """Фильтрует список по региону"""
        filter_area = []
        for vacancy in Vacancy.all_vacancies:
            if vacancy.area == key_area:
                filter_area.append(vacancy)
        return filter_area

    @classmethod
    def filtered_salary(cls, key_salary_from):
        """Фильтрует список по зарплате"""
        filter_salary = []
        for vacancy in Vacancy.all_vacancies:
            if vacancy.salary_from > key_salary_from:
                filter_salary.append(vacancy)


class JSONSaver:
    """Класс для работы с JSON файлами"""
    def __init__(self, filename):
        self.filename = filename

    def create_file(self, all_vacancies):
        """Сохраняет информацию в JSON формате"""
        with open(self.filename + ".json", "w") as file:
            for vacancy in all_vacancies:
                json.dump(vacancy, file, indent=2, ensure_ascii=False, cls=VacancyEncoder)

    def select_all(self):
        """Функция для чтения JSON формата"""
        with open(self.filename, "r") as f:
            data = json.load(f)
            for x in data:
                Vacancy(x["area"], x["salary_from"], x["salary_to"], x["requirement"],
                        x["professional_name"], x["id"], x["url"])


class VacancyEncoder(json.JSONEncoder):
    """Класс позволяет сериализовать объекты Python в формат JSON."""
    def default(self, obj):
        if isinstance(obj, Vacancy):
            return {"area": obj.area,
                    "salary_from": obj.salary_from,
                    "salary_to": obj.salary_to,
                    "requirement": obj.requirement,
                    "professional_name": obj.professional_name,
                    "id": obj.id,
                    "url": obj.url}
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)