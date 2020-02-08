from pathlib import Path
from scipy import ndimage
import PIL.Image
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from io import BytesIO
#загружаем модель
hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/1')
#для каждого пользователя своя переменная:
content_image = {}
style_image = {}
stylized_image = {}
#загрузка изображения
def load_img(img):
    max_dim = 512
    img = tf.image.decode_image(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)

    shape = tf.cast(tf.shape(img)[:-1], tf.float32)
    long_dim = max(shape)
    scale = max_dim / long_dim

    new_shape = tf.cast(shape * scale, tf.int32)

    img = tf.image.resize(img, new_shape)
    img = img[tf.newaxis, :]
    return img

def imshow(image, title=None):
    if len(image.shape) > 3:
        image = tf.squeeze(image, axis=0)

    plt.imshow(image)
    if title:
        plt.title(title)

#переводим тензор в изображение
def tensor_to_image(tensor):
    tensor = tensor*255
    tensor = np.array(tensor, dtype=np.uint8)
    if np.ndim(tensor)>3:
        assert tensor.shape[0] == 1
        tensor = tensor[0]
    return PIL.Image.fromarray(tensor)

#обработка изображений
def photo_connect(photo_one, photo_two, user_id, im_name_3):
    content_image[user_id] = load_img(photo_one) #загружаем изображение 
    style_image[user_id] = load_img(photo_two) #
    #пропускаем изображения через модель
    stylized_image[user_id] = hub_module(tf.constant(content_image[user_id]), tf.constant(style_image[user_id]))[0] 
    im_name_3[str(user_id)+'out'] = tensor_to_image(stylized_image[user_id])    #переводим тензор в изображения
    im_name_3[user_id] = BytesIO() #переводим в bytesio и конвертируем в png формат
    im_name_3[str(user_id)+'out'].save(im_name_3[user_id] , format='PNG')
    im_name_3[user_id].seek(0)
