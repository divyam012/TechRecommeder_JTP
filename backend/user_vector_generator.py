def generate_laptop_vector(budget, use_case, cpu_encoder, gpu_encoder, os_encoder):
    # Base specs for reference
    base_screen_size = 14.0
    base_ram = 4
    base_storage = 256

    # Use case adjustments
    use_case_dict = {
        'basic':    {'ram_mult': 1, 'storage_mult': 1, 'cpu_factor': 1},
        'office':   {'ram_mult': 1.5, 'storage_mult': 1.5, 'cpu_factor': 1.2},
        'professional': {'ram_mult': 2, 'storage_mult': 2, 'cpu_factor': 1.3},
        'gaming':   {'ram_mult': 3, 'storage_mult': 2, 'cpu_factor': 1.5},
    }

    uc = use_case_dict.get(use_case.lower(), use_case_dict['basic'])

    ram = base_ram * uc['ram_mult']
    storage = base_storage * uc['storage_mult']
    cpu_factor = uc['cpu_factor']

    # Example fixed choices for categorical features:
    cpu_brand = 'Intel'
    gpu_brand = 'Nvidia'
    os_name = 'windows'

    cpu_enc = cpu_encoder.transform([cpu_brand])[0]
    gpu_enc = gpu_encoder.transform([gpu_brand])[0]
    os_enc = os_encoder.transform([os_name])[0]

    # Screen size adjusted slightly by cpu_factor for example
    screen_size = base_screen_size + (cpu_factor - 1) * 1.5

    # Scale budget down similar to preprocessing (price / 10,000)
    price_scaled = budget / 10000

    # Optionally give price more weight by multiplying
    price_scaled_weighted = price_scaled * 5  # tune 5 to higher/lower as needed

    return [
        screen_size,
        ram,
        storage,
        cpu_enc,
        gpu_enc,
        os_enc,
        price_scaled_weighted
    ]
