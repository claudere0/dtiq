# Инструкция для запуска экспериментов на Acer Nitro (Windows)

Здесь собраны все шаги, чтобы прогнать новые тесты для **YOLOv8n**, **YOLOv8m** и **RT-DETR-L**, а затем закинуть результаты обратно на Mac через GitHub. Мы также прогоним заново `YOLOv8n`, чтобы собрать для нее новые метрики (mAP по размерам объектов).

## 0. Подготовка окружения
Окружение под видеокарту RTX 4050 настроено в **Python 3.11** (команда `py -3.11`).
Убедись, что ты клонировал репозиторий. Все команды запускаются через `py -3.11`.

*Примечание про веса моделей:* Тебе **не нужно** скачивать веса (`yolov8n.pt`, `yolov8m.pt` и `rtdetr-l.pt`) вручную. Библиотека `ultralytics` скачает их сама при первом запуске!

## 1. Запуск экспериментов

Я подготовил три конфигурационных файла специально для твоей видеокарты (device: 0, workers: 4, batch: 16/8). 

Запускай их по очереди (каждый тест займет какое-то время):

**Для YOLOv8n (batch 16):**
```powershell
py -3.11 scripts/validate/03_run_all_validations.py --experiment-config configs/experiment_5k_yolov8n.yaml
```

**Для YOLOv8m (batch 16):**
```powershell
py -3.11 scripts/validate/03_run_all_validations.py --experiment-config configs/experiment_5k_yolov8m.yaml
```

**Для RT-DETR-L (batch 8):**
```powershell
py -3.11 scripts/validate/03_run_all_validations.py --experiment-config configs/experiment_5k_rtdetr_l.yaml
```

> **Важно!** Если во время запуска возникнет ошибка **CUDA Out of Memory**, просто открой нужный `.yaml` файл в папке `configs/` и уменьши параметр `batch` в два раза (например, с 16 до 8, или с 8 до 4).

## 2. Сбор метрик
После того как валидация пройдет для всех моделей, собери метрики в CSV файлы:

```powershell
py -3.11 scripts/analyze/04_collect_metrics.py --experiment-config configs/experiment_5k_yolov8n.yaml
py -3.11 scripts/analyze/04_collect_metrics.py --experiment-config configs/experiment_5k_yolov8m.yaml
py -3.11 scripts/analyze/04_collect_metrics.py --experiment-config configs/experiment_5k_rtdetr_l.yaml
```

Результаты сохранятся в:
- `results/val5k_yolov8n/summary/metrics.csv`
- `results/val5k_yolov8m/summary/metrics.csv`
- `results/val5k_rtdetr_l/summary/metrics.csv`

*(Все тяжелые папки, например с результатами предсказаний и изображениями, можно оставить на Windows, нам для статьи нужны только итоговые `metrics.csv`).*

## 3. Отправка результатов на Mac через GitHub
Чтобы я (твой помощник на Маке) мог увидеть новые `metrics.csv` и встроить их в статью, выполни эти команды в PowerShell:

```powershell
# Добавляем все изменения (новые конфиги, новые csv)
git add .

# Делаем коммит
git commit -m "Add YOLOv8n, YOLOv8m and RT-DETR-L experiment results"

# Отправляем в репозиторий
git push
```

Всё! Как только сделаешь `git push`, возвращайся сюда в чат и скажи мне об этом. Я сам сделаю `git pull` на Маке и мы приступим к обновлению текста статьи и графиков.
