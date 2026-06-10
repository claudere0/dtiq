from ultralytics.data.converter import convert_coco

convert_coco(
    labels_dir="../../data/source/coco/annotations/",
    use_segments=False
)

#after running that script /coco_converted folder appear, inside that folder you can find all validation annotations