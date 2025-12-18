import os
import sys
import argparse
from use_cases.extract_plan import extract_plan_from_image
from interfaces.output_formatter import format_plan_to_json
from adapters.visualizer import visualize_plan


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured plan from image")
    parser.add_argument("--input", default="samples",
                        help="Path to input image or directory (default: ./samples)")
    parser.add_argument("--output", default="output",
                        help="Output directory for JSON and visualizations")
    parser.add_argument("--visualize", action="store_true",
                        help="Save visualized results (default: False)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if os.path.isdir(args.input):
        image_paths = [os.path.join(args.input, f) for f in os.listdir(args.input)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    else:
        image_paths = [args.input]

    if not image_paths:
        print(f"⚠️  No images found in {args.input}")
        return

    for img_path in image_paths:
        try:
            plan = extract_plan_from_image(img_path)
            json_str = format_plan_to_json(plan)
            json_path = os.path.join(
                args.output, os.path.basename(img_path) + ".json")
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"✅ JSON saved: {json_path}")

            if args.visualize:
                viz_out = os.path.join(
                    args.output, "visualizations", os.path.basename(img_path))
                visualize_plan(plan, viz_out)
                print(f"🖼  Visualization saved: {viz_out}")

        except Exception as e:
            print(f"❌ Failed on {img_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
