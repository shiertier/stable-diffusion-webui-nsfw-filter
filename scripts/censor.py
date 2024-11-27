import torch
import numpy as np
from PIL import Image
from imgutils.detect import detect_censors
from modules import scripts, shared
import os.path

# 设置填充图片路径
warning_image = os.path.join("extensions", "stable-diffusion-webui-nsfw-filter", "warning", "warning.png")

def numpy_to_pil(images):
    """
    Convert a numpy image or a batch of images to a PIL image.
    """
    if images.ndim == 3:
        images = images[None, ...]
    images = (images * 255).round().astype("uint8")
    pil_images = [Image.fromarray(image) for image in images]
    return pil_images

def check_safety(x_image, sensitivity: float):
    """
    使用 imgutils.detect.censor 检测 NSFW 内容
    """
    # 将numpy数组转换为PIL图像
    pil_image = Image.fromarray((x_image[0] * 255).astype('uint8'))
    
    try:
        # sensitivity直接作为置信度阈值使用
        conf_threshold = sensitivity
        
        detections = detect_censors(
            pil_image,
            level='s',  
            conf_threshold=conf_threshold
        )
        
        if len(detections) > 0:
            print('NSFW content detected')
            return x_image, True
        
        return x_image, False
        
    except Exception as e:
        print(f"NSFW detection error: {str(e)}")
        return x_image, False

def censor_batch(x, sensitivity: float):
    x_samples_ddim_numpy = x.cpu().permute(0, 2, 3, 1).numpy()
    x_checked_image, has_nsfw = check_safety(x_samples_ddim_numpy, sensitivity)
    
    if has_nsfw:
        try:
            hwc = x.shape
            warning = Image.open(warning_image).convert("RGB").resize((hwc[3], hwc[2]))
            warning = (np.array(warning) / 255.0).astype("float32")
            warning = torch.from_numpy(warning)
            warning = torch.unsqueeze(warning, 0).permute(0, 3, 1, 2)
            x[0] = warning
        except Exception as e:
            print(f"Warning image processing error: {str(e)}")
    
    return x

class NsfwCheckScript(scripts.Script):
    def title(self):
        return "NSFW check"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def postprocess_batch(self, p, *args, **kwargs):
        """
        Args:
            p:
            *args:
                args[0]: enable_nsfw_filter. True: 启用NSFW过滤; False: 禁用NSFW过滤
                args[1]: sensitivity: NSFW检测的灵敏度
        """
        images = kwargs['images']
        if args[0] is True:
            images[:] = censor_batch(images, args[1])[:]

    def ui(self, is_img2img):
        import gradio as gr
        enable_nsfw_filter = gr.Checkbox(
            label='Enable NSFW filter',
            value=False,
            elem_id=self.elem_id("enable_nsfw_filter")
        )
        sensitivity = gr.Slider(
            label="NSFW Detection Sensitivity",
            minimum=0.1,
            maximum=0.99,
            value=0.3,
            step=0.01,
            elem_id=self.elem_id("sensitivity")
        )
        return [enable_nsfw_filter, sensitivity]
