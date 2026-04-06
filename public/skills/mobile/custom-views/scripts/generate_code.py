#!/usr/bin/env python3
"""Generate custom view registration code for Airship Thomas scenes.

Usage:
    python generate_code.py --platform ios --class WeatherWidget --identifier weather_widget
    python generate_code.py --platform android --class MapView --identifier map_view --properties '{"lat": 0.0, "lng": 0.0}'
"""

import argparse
import json
import re
import yaml
from typing import Dict, Any, Optional


def pascal_to_snake(name: str) -> str:
    """Convert PascalCase to snake_case."""
    snake = re.sub('([A-Z])', r'_\1', name).lower()
    return snake.lstrip('_')


def swift_type(value: Any) -> str:
    """Map Python value to Swift type."""
    if isinstance(value, bool):
        return "Bool"
    elif isinstance(value, int) or isinstance(value, float):
        return "Double"
    elif isinstance(value, str):
        return "String"
    elif isinstance(value, list):
        return "[AirshipJSON]"
    elif isinstance(value, dict):
        return "AirshipJSON"
    return "Any"


def swift_default(value: Any) -> str:
    """Generate Swift default value."""
    if isinstance(value, bool):
        return "false"
    elif isinstance(value, (int, float)):
        return "0"
    elif isinstance(value, str):
        return '""'
    elif isinstance(value, list):
        return "[]"
    elif isinstance(value, dict):
        return "[:]"
    return '""'


def kotlin_accessor(value: Any) -> str:
    """Map Python value to Kotlin JsonValue accessor."""
    if isinstance(value, bool):
        return ".boolean"
    elif isinstance(value, int):
        return ".int"
    elif isinstance(value, float):
        return ".double"
    elif isinstance(value, str):
        return ".string"
    elif isinstance(value, list):
        return ".list"
    elif isinstance(value, dict):
        return ".map"
    return ".string"


def kotlin_default(value: Any) -> str:
    """Generate Kotlin default value."""
    if isinstance(value, bool):
        return f"?: {str(value).lower()}"
    elif isinstance(value, (int, float)):
        return f"?: {value}"
    elif isinstance(value, str):
        return f'?: "{value}"'
    return ""


def generate_ios_code(class_name: str, identifier: str, properties: Optional[Dict[str, Any]] = None) -> str:
    """Generate iOS (Swift) registration code."""
    code = f'''// Add this to your app initialization (e.g., AppDelegate or App struct)
import AirshipCore

// Register your custom view
AirshipCustomViewManager.shared.register(name: "{identifier}") {{ args in
    {class_name}(properties: args.properties)
}}'''

    if properties:
        prop_lines = []
        for prop_name, value in properties.items():
            stype = swift_type(value)
            default = swift_default(value)
            prop_lines.append(f'        let {prop_name} = properties?["{prop_name}"]?.unWrap() as? {stype} ?? {default}')

        code += f'''

// Your {class_name} should accept properties parameter
struct {class_name}: View {{
    let properties: AirshipJSON?

    var body: some View {{
        // Access properties:
{chr(10).join(prop_lines)}

        // Your view implementation here
        Text("Custom View")
    }}
}}'''

    return code


def generate_android_code(class_name: str, identifier: str, properties: Optional[Dict[str, Any]] = None) -> str:
    """Generate Android (Kotlin) registration code."""
    code = f'''// Add this to your Application.onCreate()
import com.urbanairship.android.layout.ui.AirshipCustomViewManager

// Register your custom view
AirshipCustomViewManager.shared().register("{identifier}") {{ args ->
    {class_name}(properties = args.properties)
}}'''

    if properties:
        prop_lines = []
        for prop_name, value in properties.items():
            accessor = kotlin_accessor(value)
            default = kotlin_default(value)
            prop_lines.append(f'    val {prop_name} = properties?.get("{prop_name}")?{accessor} {default}')

        code += f'''

// Your {class_name} should accept properties parameter
@Composable
fun {class_name}(properties: JsonMap?) {{
    // Access properties:
{chr(10).join(prop_lines)}

    // Your composable implementation here
    Text("Custom View")
}}'''

    return code


def generate_scene_yaml(identifier: str, properties: Optional[Dict[str, Any]] = None) -> str:
    """Generate Thomas scene YAML snippet."""
    scene_dict = {
        "view": {
            "type": "custom_view",
            "name": identifier
        }
    }

    if properties:
        scene_dict["view"]["properties"] = properties

    return yaml.dump(scene_dict, default_flow_style=False, sort_keys=False)


def main():
    parser = argparse.ArgumentParser(
        description="Generate custom view registration code for Airship Thomas scenes."
    )
    parser.add_argument(
        "-p", "--platform",
        required=True,
        choices=["ios", "android"],
        help="Target platform"
    )
    parser.add_argument(
        "-c", "--class",
        dest="class_name",
        required=True,
        help="Custom view class name (e.g., WeatherWidget)"
    )
    parser.add_argument(
        "-i", "--identifier",
        help="Registration identifier (defaults to snake_case of class name)"
    )
    parser.add_argument(
        "--properties",
        help="JSON string of properties (e.g., '{\"title\": \"Hello\", \"count\": 42}')"
    )
    parser.add_argument(
        "--yaml",
        action="store_true",
        help="Also output Thomas scene YAML snippet"
    )

    args = parser.parse_args()

    # Default identifier from class name
    identifier = args.identifier or pascal_to_snake(args.class_name)

    # Parse properties if provided
    properties = None
    if args.properties:
        try:
            properties = json.loads(args.properties)
        except json.JSONDecodeError as e:
            print(f"Error parsing properties JSON: {e}")
            return 1

    # Generate code
    print(f"\n{'='*60}")
    print(f"Custom View: {args.class_name}")
    print(f"Identifier: {identifier}")
    print(f"Platform: {args.platform.upper()}")
    print(f"{'='*60}\n")

    if args.platform == "ios":
        code = generate_ios_code(args.class_name, identifier, properties)
    else:
        code = generate_android_code(args.class_name, identifier, properties)

    print("## Registration Code\n")
    print("```" + ("swift" if args.platform == "ios" else "kotlin"))
    print(code)
    print("```\n")

    if args.yaml or properties:
        print("## Thomas Scene YAML\n")
        print("```yaml")
        print(generate_scene_yaml(identifier, properties))
        print("```\n")

    return 0


if __name__ == "__main__":
    exit(main())
