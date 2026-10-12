# Successful Cases Source Files

This package contains all the source files used to generate the `successful_cases_dashboard.html` comparison report for mask-guided object removal with Qwen Image 3.0.

## Folder Layout

### 01_generator_script
Contains the Python script that compiles everything into the final HTML dashboard.

- `compile_successful_cases_dashboard.py` — reads the prompts, input images, masks, and model outputs; embeds them as JPEG/base64; and writes a self-contained HTML file.

### 02_base_model_outputs
Output images produced by the base model, `qwen-image-3.0`.

- `hike_output_sample2.png`
- `penguin_output.png`
- `selfie_output_sample1.png`
- `soda_output_sample2.png`

### 03_pro_model_outputs
Output images produced by the pro model, `qwen-image-3.0-pro`.

- `hike_output_sample1.png`
- `penguin_output_sample3.png`
- `selfie_output_sample2.png`
- `soda_output_sample1.png`

### 04_prompts
The text prompts that were sent to the model for each case.

- `hike-prompt.txt`
- `penguin-prompt.txt`
- `selfie-prompt.txt`
- `soda-prompt.txt`

Each prompt follows the mask-first pattern: Image 1 is the source photo, Image 2 is the binary mask, and the white pixels mark the region to remove.

### 05_input_images_and_masks
The original input photos and their corresponding removal masks.

- `hike.jpg` / `hike_mask.png`
- `penguin.jpg` / `penguin_mask.png`
- `selfie.jpg` / `selfie_mask.png`
- `soda.jpg` / `soda_mask.png`

## How the Pieces Work Together

1. **Inputs and masks** (`05_input_images_and_masks`) define what each test case looks like and which region should be removed.
2. **Prompts** (`04_prompts`) describe the editing instruction for each case.
3. The Qwen Image 3.0 API receives the input image, mask, and prompt, then produces the edited output images.
4. **Base outputs** (`02_base_model_outputs`) and **pro outputs** (`03_pro_model_outputs`) are the two models' results for the same case and prompt.
5. **Generator script** (`01_generator_script`) combines all of the above into one self-contained HTML dashboard with side-by-side comparisons.

## Regenerating the Dashboard

```bash
python3 compile_successful_cases_dashboard.py
```

The script expects this folder layout and will write `successful_cases_dashboard.html` in the parent workspace directory.
