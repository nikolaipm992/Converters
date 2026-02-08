# Universal File Converter (Windows Context Menu)

## Описание

Universal File Converter — это инструмент, позволяющий конвертировать файлы различных форматов (изображения, видео, аудио, PDF) через контекстное меню Windows. После установки, пользователь может кликнуть правой кнопкой мыши по любому файлу, выбрать "Конвертировать файл", и получить список доступных действий, которые можно выполнить с этим файлом.

## Особенности

- Интеграция в контекстное меню Windows.
- Поддержка изображений, видео, аудио, PDF.
- Лёгкое добавление новых действий.
- Модульная архитектура.
- Совместимость с Python 3.10+.

## Установка

1. Убедитесь, что `ffmpeg` установлен в системе.
2. Установите зависимости: `pip install -r requirements.txt`
3. Запустите установку: `python setup.py` (от имени администратора)

## Удаление

Запустите: `python uninstall.py` (от имени администратора)

## Расширение функционала

Добавьте новый метод в `modules/converter.py`, затем зарегистрируйте его в `config.json`.

git init
git add .
git commit -m "first commit"
git branch -M master
git remote add origin https://github.com/nikolaipm992/Converters.git
git push -u origin master