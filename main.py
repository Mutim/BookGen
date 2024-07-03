import json
import os

import yaml


# Builder functions
def section_builder(page_info: tuple) -> dict:
    name = page_info[0].replace("_", " ").title()
    job = page_info[5]
    icon = page_info[0]

    job_info = {
    "parent": f"patchouli:{job}",
    "name": f"({page_info[3]}) {name.split(':')[1]}",
    "icon": icon,
    "category": f"patchouli:{job}",
    "pages": page_builder(page_info)
}

    return job_info


def page_builder(info: tuple) -> list[any]:
    item, text1, entities, level, text2, category, job_type = info
    title = item.split(":")[1].replace('_', ' ').title()
    entity = tuple(entities.split(":"))


    # This is only separated in case we want to do things different for each type. Ranching, Fishing, and Gathering are probably going to be similar, but the rest might change.
    page_list = {
        "gathering": [
            {
                "type": "patchouli:spotlight",
                "title": f"{title}!",
                "item": item_builder(item),
                "text": text1
            },
            {
                "type": "patchouli:entity",
                "entity": entity_builder(entity),
                "scale": 1,
                "offset": 0,
                "name": f"Capability Level {level}",
                "text": text2
            }
        ],
        "ranching": [
            {
                "type": "patchouli:spotlight",
                "title": f"{title}!",
                "item": item_builder(item),
                "text": text1
            },
            {
                "type": "patchouli:entity",
                "entity": entity_builder(entity),
                "scale": 0.5,
                "offset": 0,
                "name": f"Capability Level {level}",
                "text": text2
            }
        ],
        "inhand_production": [
            {
                "type": "patchouli:spotlight",
                "title": f"{title}!",
                "item": item_builder(item),
                "text": text1
            },
            {
                "type": "patchouli:entity",
                "entity": entity_builder(entity),
                "scale": 0.5,
                "offset": 0,
                "name": f"Capability Level {level}",
                "text": text2
            }
        ],
        "place_production": [
            {
                "type": "patchouli:spotlight",
                "title": f"{title}!",
                "item": item_builder(item),
                "text": text1
            },
            {
                "type": "patchouli:entity",
                "entity": entity_builder(entity),
                "scale": 0.5,
                "offset": 0,
                "name": f"Capability Level {level}",
                "text": text2
            }
        ]
    }

    return page_list[job_type]


def item_builder(item: str) -> str:
    color = "#FFA500"
    display_name = item.split(":")[1].replace('_', ' ').title()
    name_key = json.dumps({"text": display_name, "color": color}).replace('"', r'\"')

    return fr"{item}{{display:{{Name:'{name_key}'}}}}"


def entity_builder(entity_info: tuple):
    namespace, entity = entity_info
    entities = ["cow", "pig", "chicken", "sheep"]
    if entity in entities:
        return fr"{namespace}:{entity}"
    else:
        return fr'minecraft:item{{Item:{{id:"{namespace}:{entity}",Count:1b}}}}'


def file_builder(category: str, item: str, contents: tuple):
    file_contents, category_contents = contents
    entry_path = rf".\patchouli_books\avalon_capabilities_record\en_us\entries\{category}"
    category_path = rf".\patchouli_books\avalon_capabilities_record\en_us\categories"

    os.makedirs(category_path, exist_ok=True)
    with open(fr'{category_path}\{category}.json', 'w+') as f:
        json.dump(category_contents, f, indent=2)

    os.makedirs(entry_path, exist_ok=True)
    with open(fr'{entry_path}\{category}_{item}.json', 'w+') as f:
        json.dump(file_contents, f, indent=2)


def make_category(icon: str, name: str):

    contents = {
    "name": name.title(),
    "description": F"Default category. Please change in categories/{name}",
    "icon": icon
}
    return contents


# Some helper functions
def read_yaml(file_path: str) -> dict:
    with open(file_path, 'r') as yaml_info:
        yaml_obj = yaml.safe_load(yaml_info)

    return yaml_obj


def suffix(n):
    if 11 <= n % 100 <= 13:
        return "th"
    else:
        suf = {
            1: 'st',
            2: 'nd',
            3: 'rd'
        }
        return suf.get(n % 10, 'th')


# Type Handlers.  Might be best to move to a class, and instantiate each from there......baah
def gathering_handler(capability):
    harvests = capability["harvests"]
    category = capability["category"]
    job_type = capability["type"]
    category_icon = capability["icon"]

    for index, j in enumerate(harvests):
        order_unlocked = index + 1
        level = harvests[j]["capability_needed"]
        item = harvests[j]["material_given"]

        icon = harvests[j]["icon"]
        spotlight = harvests[j]["spotlight"]

        read_item = item.split('_', maxsplit=1)[1].replace('_', ' ').title()

        t1 = f"Gathering $(#FFA500){read_item} $()is simple! This is the {order_unlocked}{suffix(order_unlocked)} capability that you will unlock! $(br2)Item Given: {read_item}"
        t2 = f"At $(#FFA500)level {level}$(), you will be able to immediately gather $(#FFA500){read_item}$()"

        info = icon, t1, spotlight, level, t2, category, job_type
        file_contents = section_builder(info)
        category_contents = make_category(category_icon, category)
        file_builder(category, item, (file_contents, category_contents))


def ranching_handler(capability):
    harvests = capability["harvests"]
    category = capability["category"]
    job_type = capability["type"]
    category_icon = capability["icon"]

    for index, j in enumerate(harvests):
        order_unlocked = index + 1
        for t in harvests[j]:
            tool = harvests[j][t]["tool"]
            level = harvests[j][t]["capability_needed"]
            item = harvests[j][t]["material_given"]
            icon = harvests[j][t]["icon"]
            spotlight = harvests[j][t]["spotlight"]
            read_item = item.split('_', maxsplit=1)[1].replace('_', ' ').title()

            t1 = (f"Ranching for $(#FFA500){read_item} $()is simple! This is the {order_unlocked}{suffix(order_unlocked)} "
                  f"capability that you will unlock! $(br2)"
                  f"Animal Ranched: {j.title()}$(br)"
                  f"Item Given: {read_item}$(br)"
                  f"Tool Required: {'Hand' if tool == 'air' else tool.title()}")
            t2 = f"At $(#FFA500)level {level}$(), you will be able to immediately gather $(#FFA500){read_item}$()"

            info = icon, t1, spotlight, level, t2, category, job_type
            file_contents = section_builder(info)
            category_contents = make_category(category_icon, category)

            file_builder(category, item, (file_contents, category_contents))


def inhand_production_handler(capability):
    crafts = capability["crafts"]
    category = capability["category"]
    job_type = capability["type"]
    category_icon = capability["icon"]

    for index, j in enumerate(crafts):
        order_unlocked = index + 1

        level = crafts[j]["capability_needed"]
        item = crafts[j]["material_given"]
        icon = crafts[j]["icon"]
        spotlight = crafts[j]["spotlight"]
        read_item = item.split('_', maxsplit=1)[1].replace('_', ' ').title()

        t1 = (f"Producing $(#FFA500){read_item} $()is simple! This is the {order_unlocked}{suffix(order_unlocked)} "
              f"capability that you will unlock! $(br2)"
              f"Item Given: {read_item}$(br)")
        t2 = f"At $(#FFA500)level {level}$(), you will be able to immediately produce $(#FFA500){read_item}$()"

        info = icon, t1, spotlight, level, t2, category, job_type
        file_contents = section_builder(info)
        category_contents = make_category(category_icon, category)

        file_builder(category, item, (file_contents, category_contents))


def place_production_handler(capability):
    materials = capability["materials"]
    category = capability["category"]
    job_type = capability["type"]
    category_icon = capability["icon"]

    for index, j in enumerate(materials):
        order_unlocked = index + 1
        for t in materials[j]:
            tool = materials[j][t]["tool"]
            level = materials[j][t]["capability_needed"]
            item = materials[j][t]["material_given"]
            icon = materials[j][t]["icon"]
            spotlight = materials[j][t]["spotlight"]
            read_item = item.split('_', maxsplit=1)[1].replace('_', ' ').title()

            t1 = (f"Producing for $(#FFA500){read_item} $()is simple! This is the {order_unlocked}{suffix(order_unlocked)} "
                  f"capability that you will unlock! $(br2)"
                  f"Animal Ranched: {j.title()}$(br)"
                  f"Item Given: {read_item}$(br)"
                  f"Tool Required: {'Hand' if tool == 'air' else tool.title()}")
            t2 = f"At $(#FFA500)level {level}$(), you will be able to immediately gather $(#FFA500){read_item}$()"

            info = icon, t1, spotlight, level, t2, category, job_type
            file_contents = section_builder(info)
            category_contents = make_category(category_icon, category)

            file_builder(category, item, (file_contents, category_contents))


def fishing_handler(capability):
    harvests = capability["harvests"]
    category = capability["category"]
    job_type = capability["type"]
    category_icon = capability["icon"]

    for index, j in enumerate(harvests):
        order_unlocked = index + 1
        for t in harvests[j]:
            level = harvests[j][t]["capability_needed"]
            item = harvests[j][t]["material_given"]

            icon = harvests[j][t]
            spotlight = harvests[j][t]

            read_item = item.split('_', maxsplit=1)[1].replace('_', ' ').title()

            # Create tuple of info for t
            t1 = f"Gathering $(#FFA500){read_item} $()is simple! This is the {order_unlocked}{suffix(order_unlocked)} capability that you will unlock! $(br2)Item Given: {read_item}"
            t2 = f"At $(#FFA500)level {level}$(), you will be able to immediately gather $(#FFA500){read_item}$()"

            info = icon, t1, spotlight, level, t2, category, job_type
            file_contents = section_builder(info)
            category_contents = make_category(category_icon, category)
            file_builder(category, item, (file_contents, category_contents))


# Mapping from type to handler function
handler_mapping = {
    "gathering": gathering_handler,
    "ranching": ranching_handler,
    "inhand_production": inhand_production_handler,
    "place_production": place_production_handler,
    "fishing": fishing_handler
}


if __name__ == "__main__":
    capabilities = read_yaml('jobs.yaml')["capabilities_data"]["capability"]

    for key, capability in capabilities.items():
        capability_type = capability.get("type")
        handler = handler_mapping.get(capability_type)
        if handler:
            handler(capability)
        else:
            print(f"No handler found for capability type: {capability}")
