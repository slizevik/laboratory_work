# Лабораторная работа №4

1.Активируйте окружение: .venv\Scripts\activate (Windows) или source .venv\Scripts\activate (Linux/Mac)

2.Установите зависимости: pip install -r requirements.txt

3.Запустите приложение: python main.py

4.Запуск тестов из папки test 
pytest tests/

5. только юнит-тесты
pytest tests/test_models/ tests/test_repositories/ tests/test_services/

6. Только API тесты
   pytest tests/test_controllers/

7. Покрытие тестами
pytest --cov=. --cov-report=html

 8. Параллельные тесты
pytest -n auto
