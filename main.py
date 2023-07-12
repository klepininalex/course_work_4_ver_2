from info import HH, SJ, JSONSaver, Vacancy


def main():
    hh = HH("https://api.hh.ru/vacancies")
    sj = SJ("https://api.superjob.ru/2.0/vacancies/",
            "API_KEY")
    keyword = input("Введите ключевое слово для поиска: ")
    """Ввод ключевого слова для запроса по API"""

    search_query = input("Введите платформу для поиска:"
                         "\nhh.ru -- нажмите '1',\nsuperjob.ru -- нажмите '2' "
                         "\nс двух сайтов -- нажмите '3':  ")
    """Выбор платфрма для поиска вакансий"""
    if search_query == "1":
        hh.get_formatted_vacancies(keyword)
    elif search_query == "2":
        sj.get_formatted_vacancies(keyword)
    elif search_query == "3":
        hh.get_formatted_vacancies(keyword)
        sj.get_formatted_vacancies(keyword)
    else:
        print("Введите правильное название платформы")
        return

    js = JSONSaver("all_vacancies")

    js.create_file(Vacancy.all_vacancies)

    top_n = int(input("Введите количество вакансий для вывода в топ N: "))
    """вывод топ вакансий по эарплате"""
    Vacancy.sort_vacancies()
    for i in range(top_n):
        print(Vacancy.all_vacancies[i], end="\n")

    filter_data = input("Если хотите вывести полный список вакансий - нажмите 1"
                        "\nесли хотите отфильтровать по региону - нажмите 2"
                        "\nесли хотите отфильтровать по зарплате - нажмите 3")
    """Выбор фильтрации по региону, зарплате или вывод всех вакансий"""
    if filter_data == "1":
        print(Vacancy.all_vacancies)
    elif filter_data == "2":
        filter_area = input("Введите название города для фильтрации по региону  ")

        print(*Vacancy.filtered_area(filter_area))
    elif filter_data == "3":
        while True:
            try:
                filter_salary = input("Введите ожидаемую сумму ")
                filter_salary = int(filter_salary)
                Vacancy.filtered_salary(filter_salary)
                print(*Vacancy.all_vacancies)
                break
            except ValueError:
                print("Невалидное значение")


if __name__ == "__main__":
    main()