import shutil
from pathlib import Path
from ultralytics.data.converter import convert_coco

def main():
    # Resolve project root dynamically
    root_dir = Path(__file__).resolve().parents[2]
    coco_dir = root_dir / "data" / "source" / "coco"
    annotations_dir = coco_dir / "annotations"
    
    if not annotations_dir.exists():
        print(f"Error: Cannot find annotations at {annotations_dir}")
        return

    print("Converting COCO annotations to YOLO format...")
    # Ultralytics convert_coco will look for .json files here
    convert_coco(
        labels_dir=str(annotations_dir),
        use_segments=False
    )
    
    # ultralytics creates 'coco_converted' adjacent to the provided labels_dir
    coco_converted_dir = coco_dir / "coco_converted"
    
    if coco_converted_dir.exists():
        labels_src = coco_converted_dir / "labels"
        labels_dst = coco_dir / "labels"
        
        # Remove existing labels folder if it exists
        if labels_dst.exists():
            shutil.rmtree(labels_dst)
            
        # Move newly generated labels
        if labels_src.exists():
            shutil.move(str(labels_src), str(labels_dst))
            print(f"Successfully generated and moved labels to: {labels_dst}")
            
        # Clean up the temporary folder
        shutil.rmtree(coco_converted_dir)
        print("Cleaned up temporary coco_converted directory.")
    else:
        print("Warning: Could not find 'coco_converted' directory after conversion.")

if __name__ == "__main__":
    main()