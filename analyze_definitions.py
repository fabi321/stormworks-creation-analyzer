from __future__ import annotations
import re
from xml.etree import ElementTree as ET
from pathlib import Path
from typing import Optional, TypedDict
from sys import stderr
import json

import requests
from bs4 import BeautifulSoup, Tag


definition_path: Path = Path('~/.steam/steam/steamapps/common/Stormworks/rom/data/definitions')
WIKI_BASE: str = 'https://stormworks.fandom.com/wiki/Wiki/Building/Components/'
WIKI_SITES: tuple[str, ...] = (
    'Blocks', 'Vehicle_Control', 'Mechanics', 'Propulsion', 'Person_Operations', 'Radio', 'Fluids', 'Logic',
    'User_Input', 'Electricity', 'Displays', 'Sound', 'Sensors', 'Decorative', 'Video/Monitors', 'Video/Cameras'
)
WIKI_NAMES_TO_GAME_NAMES: dict[str, str] = {
    'window_1x1_inverted_pyramid': 'window_1x1_inv_pyramid',
    'window_large_(3x3)': 'window_large',
    'window_narrow_(1x3)': 'window_narrow',
    'window_large_angled': 'window_large_angle',
    'window_narrow_angled': 'window_narrow_angle',
    'window_large_corner': 'window_corner_2',
    'window_small_angled': 'window_small_angle',
    'wheel_3x3_suspension': 'wheel_advanced_3_sus',
    'wheel_5x5_suspension': 'wheel_advanced_5_sus',
    'wheel_7x7_suspension': 'wheel_advanced_7_sus',
    'wheel_9x9_suspension': 'wheel_advanced_9_sus',
    'tank_wheel_large': 'wheel_tank_7',
    'tank_wheel_medium': 'wheel_tank_5',
    'tank_wheel_small': 'wheel_tank_1',
    'tank_drive_wheel_large': 'wheel_tank_drive_7',
    'tank_drive_wheel_medium': 'wheel_tank_drive_5',
    'tank_drive_wheel_small': 'wheel_tank_drive_1',
    'wing_front_section': 'wing_small_front',
    'linear_track_base_small': 'linear_compact_base',
    'linear_track_extension_small': 'linear_compact_module',
    'magnet': 'magall',
    'piston': 'linear_matic_a',
    'robotic_pivot_power': 'multibody_robotic_pivot_01_a',
    'robotic_pivot_fluid': 'multibody_robotic_pivot_01_a_fluid',
    'winch_small': 'rope_hook_winch',
    'winch_large': 'rope_hook_winch_large',
    'jet_intake_small': 'jet_engine_intake_small',
    'jet_intake_medium': 'jet_engine_intake_large',
    'jet_duct_t-piece': 'jet_engine_duct_t',
    'jet_duct_corner': 'jet_engine_duct_angle',
    'jet_exhaust_basic': 'jet_engine_exhaust_basic',
    'gearbox': 'torque_gearbox',
    'rotor_heavy': 'rotor_coaxial_prop_end',
    'ducted_fan_small': 'fan_small',
    'ducted_fan_large': 'fan_large',
    'propeller_small': 'propeller',
    'propeller_large': 'large_propeller',
    'propeller_giant': 'giga_prop_small',
    'solid_rocket_booster_huge': 'solid_rocket_nozzle_huge',
    'solid_rocket_booster_large': 'solid_rocket_nozzle_large',
    'solid_rocket_booster_medium': 'solid_rocket_nozzle_medium',
    'solid_rocket_booster_small': 'solid_rocket_nozzle_small',
    'solid_rocket_fuel_huge': 'solid_rocket_huge',
    'solid_rocket_fuel_large': 'solid_rocket_large',
    'solid_rocket_fuel_medium': 'solid_rocket_medium',
    'solid_rocket_fuel_small': 'solid_rocket_small',
    'train_wheel_assembly': 'train_wheels',
    'outfit_inventory_scuba': 'inventory_outfit_scuba',
    'outfit_inventory_diving': 'inventory_outfit_diving',
    'outfit_inventory_parachute': 'inventory_outfit_parachute',
    'outfit_inventory_firefighter': 'inventory_outfit_firefighter',
    'outfit_inventory_arctic': 'inventory_outfit_arctic',
    'outfit_inventory_empty': 'inventory_outfit',
    'pipe_t-piece': 'trans_t',
    'pipe_t-pice_corner': 'trans_t_corner',
    'enclosed_pipe_straight': 'trans_block_straight',
    'enclosed_pipe_angle': 'trans_block_angle',
    'enclosed_pipe_t-piece': 'trans_block_t',
    'enclosed_pipe_t-pice_corner': 'trans_block_t_corner',
    'enclosed_pipe_cross': 'trans_block_cross',
    'enclosed_pipe_cross_corner': 'trans_block_cross_corner',
    'enclosed_pipe_omni': 'trans_block_omni',
    'tank_small': 'fluid_tank_small',
    'tank_medium': 'fluid_tank_medium',
    'tank_large': 'fluid_tank_large',
    'fluid_valve_on/off': 'fluid_valve_on_off',
    'fluid_flow_valve_(directional)': 'fluid_valve_flow',
    'fluid_pump_large': 'water_pump_large',
    'hose': 'water_hose',
    'anchor_fluid_hose': 'rope_hook_fluid',
    'constant_on': 'gate_bool_constant',
    'function_(3_input)': 'gate_function_large',
    'memory': 'gate_float_register',
    'keypad_small': 'button_keypad_small',
    'keypad_large': 'button_keypad_large',
    'pilot_seat_compact': 'seat_compact',
    'anchor_electrical_cable': 'rope_hook_composite',
    'artifical_horizon': 'artificial_horizon',
    'speaker_small': 'speaker',
    'megaphone_speaker_small': 'speaker_medium',
    'megaphone_speaker_large': 'speaker_large',
    'temperature_sensor': 'temperature_probe',
    'gps': 'gps_sensor',
    'sonar': 'radar_sonar_small',
    'railing_corner': 'railing_segment_corner',
    'railing_corner_diagonal': 'railing_segment_corner_diag',
    'railing_curve': 'railing_segment_curve',
    'railing_end': 'railing_segment_end',
    'railing_end_diagonal': 'railing_segment_end_diag',
    'railing_straight': 'railing_segment_extension',
    'railing_straight_diagonal': 'railing_segment_extension_diag',
    'railing_incline': 'railing_segment_angle',
    'railing_middle': 'railing_segment_middle',
    'railing_middle_diagonal': 'railing_segment_middle_diag',
    'anchor_rope': 'rope_hook',
    'hud_1x1': 'monitor_hud_1',
    'hud_3x3': 'monitor_hud_3',
    'monitor_3x5': 'monitor_5',
}


class JsonDefinition(TypedDict):
    label: str
    image: str
    mass: float


class Definition:
    def __init__(self, id: str, name: str, mass: float, url: Optional[str] = None) -> None:
        self.id: str = id
        self.name: str = name
        self.mass: float = mass
        self.url: Optional[str] = url

    @staticmethod
    def from_file(filename: Path) -> Definition:
        with open(filename, 'r') as f:
            file_content: str = f.read()
            file_content = re.sub(r'([0-9]+=)', r'_\1', file_content)
            root: ET = ET.fromstring(file_content)
        assert root.tag == 'definition'
        id: str = filename.stem
        name: str = root.get('name')
        mass: float = float(root.get('mass'))
        return Definition(id, name, mass)

    def to_dict(self) -> JsonDefinition:
        return {
            'label': self.name,
            'image': self.url if self.url else '',
            'mass': self.mass if self.mass % 1 != 0 else int(self.mass)
        }

    def __repr__(self) -> str:
        return f'Definition(id={self.id!r}, name={self.name!r}, mass={self.mass!r}, url={self.url!r})'


def get_all_definitions() -> list[Definition]:
    files: list[Path] = [file for file in definition_path.expanduser().iterdir() if file.is_file()]
    return [Definition.from_file(file) for file in sorted(files)]


def extract_image_urls_from_wiki_site(url: str) -> dict[str, str]:
    resp: requests.Response = requests.get(url)
    assert resp.status_code == 200
    soup: BeautifulSoup = BeautifulSoup(resp.text, 'html.parser')
    main_content_div: Tag = soup.find('div', {'class': 'mw-parser-output'})
    list_div: Tag = main_content_div.find_all('div', recursive=False)[-1]
    list_items: list[Tag] = list_div.find_all('div', recursive=False)[2:]
    images: dict[str, str] = {}
    for img_div in list_items:
        name: str = img_div.get('id').lower().replace('[', '').replace(']', '').split('|')[0]
        img_url: str = img_div.find('a').get('href')
        if name in WIKI_NAMES_TO_GAME_NAMES:
            name = WIKI_NAMES_TO_GAME_NAMES[name]
        images[name] = img_url
    return images


def extend_definitions_using_images(definitions: list[Definition], images: dict[str, str]):
    for name, url in images.items():
        match: bool = False
        for definition in definitions:
            if name == definition.id or name == definition.name.lower().replace(' ', '_').replace('-', '_'):
                match = True
                definition.url = url
                break
        if not match:
            print(f'Could not find match for {name}', file=stderr)


def extract_images(definitions: list[Definition]):
    for site in WIKI_SITES:
        full_url: str = WIKI_BASE + site
        image_urls: dict[str, str] = extract_image_urls_from_wiki_site(full_url)
        extend_definitions_using_images(definitions, image_urls)


def definitions_to_json(definitions: list[Definition]) -> str:
    dict_definitions: dict[str, JsonDefinition] = {
        definition.id: definition.to_dict()
        for definition in definitions
    }
    return json.dumps(dict_definitions, indent=2)


def main():
    definitions: list[Definition] = get_all_definitions()
    extract_images(definitions)
    json_content: str = definitions_to_json(definitions)
    print(json_content)


if __name__ == '__main__':
    main()
