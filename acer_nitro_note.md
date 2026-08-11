# Инструкция для запуска экспериментов на Acer Nitro (Windows)

Здесь собраны все шаги, чтобы прогнать новые тесты для YOLOv8m и RT-DETR-L, а затем закинуть результаты обратно на Mac через GitHub.

## 0. Подготовка окружения
Убедись, что ты клонировал (или обновил через `git pull`) этот репозиторий и проверил окружение с помощью другого ИИ (CUDA, PyTorch, pycocotools, ultralytics).

*Примечание про веса моделей:* Тебе **не нужно** скачивать веса (`yolov8m.pt` и `rtdetr-l.pt`) вручную. Библиотека `ultralytics` скачает их сама при первом запуске!

## 1. Запуск экспериментов

Я подготовил два новых конфигурационных файла специально для твоей видеокарты (device: 0, workers: 4, batch: 16/8). 

**Для YOLOv8m (batch 16):**
```powershell
python scripts/validate/03_run_all_validations.py --experiment-config configs/experiment_5k_yolov8m.yaml
```

**Для RT-DETR-L (batch 8):**
```powershell
python scripts/validate/03_run_all_validations.py --experiment-config configs/experiment_5k_rtdetr_l.yaml
```

> **Важно!** Если во время запуска возникнет ошибка **CUDA Out of Memory**, просто открой нужный `.yaml` файл в папке `configs/` и уменьши параметр `batch` в два раза (например, с 16 до 8, или с 8 до 4).

## 2. Сбор метрик
После того как валидация пройдет для всех форматов, собери метрики в CSV файлы:

```powershell
python scripts/analyze/04_collect_metrics.py --experiment-config configs/experiment_5k_yolov8m.yaml
python scripts/analyze/04_collect_metrics.py --experiment-config configs/experiment_5k_rtdetr_l.yaml
```

Результаты сохранятся в:
- `results/val5k_yolov8m/summary/metrics.csv`
- `results/val5k_rtdetr_l/summary/metrics.csv`

*(Все тяжелые папки, например с результатами предсказаний и изображениями, можно оставить на Windows, нам для статьи нужны только итоговые `metrics.csv`).*

## 3. Отправка результатов на Mac через GitHub
Чтобы я (твой помощник на Маке) мог увидеть новые `metrics.csv` и встроить их в статью, выполни эти команды в PowerShell:

```powershell
# Добавляем все изменения (новые конфиги, новые csv)
git add .

# Делаем коммит
git commit -m "Add YOLOv8m and RT-DETR-L experiment results"

# Отправляем в репозиторий
git push
```

Всё! Как только сделаешь `git push`, возвращайся сюда в чат и скажи мне об этом. Я сам сделаю `git pull` на Маке и мы приступим к обновлению текста статьи и графиков.
