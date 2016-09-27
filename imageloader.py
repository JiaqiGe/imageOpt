import urllib2
import json
import yaml
import multiprocessing as mp
import os
import errno
import logging

config = yaml.safe_load(open("config.yml"))
logging.basicConfig(level=logging.INFO)


def _hotel_gallery(hotel_id):
    try:
        hotel_summary = json.load(urllib2.urlopen(config["end_point"]["retail_summary"] + str(hotel_id)))
    except urllib2.URLError:
        pass
    return hotel_summary['pictureSet']['gallery']


def _hotel_images(hotel_id, image_type='thumbnail'):
    gallery = _hotel_gallery(hotel_id)
    images = []
    for image_summary in gallery:
        image_id = image_summary['id']
        try:
            image = image_summary[image_type]
        except Exception:
            continue

        label = image['displayText']
        url = image['path']
        images.append({'hotelId': hotel_id,
                       'imageId': image_id,
                       'label': label,
                       'url': url,
                       'imageType': image_type
                       })
    return images


def _save_image(image):
    filename = 'data/' + str(image['hotelId']) + '/' + image['label'] + '/' + image['imageType'] + str(
        image['imageId']) + '.jpg'

    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    with open(filename, 'wb') as f:
        f.write(urllib2.urlopen(config['end_point']['media_gallery'] + image['url']).read())


# def save_hotel_images(hotel_id, image_type='thumbnail'):
#     images = _hotel_images(hotel_id, image_type)
#     for image in images:
#         f = open('data/' + str(image['imageId']) + '.jpg', 'wb')
#         f.write(urllib2.urlopen(config['end_point']['media_gallery'] + image['url']).read())
#         f.close()


def save_hotel_images_parallel(hotel_id, image_type='thumbnail'):
    images = _hotel_images(hotel_id, image_type)

    pool = mp.Pool(processes=config['num_threads'])
    pool.map(_save_image, images)
    pool.close()


def _resolve_region(term):
    return json.load(urllib2.urlopen(config['end_point']['resolve_region'] + term))['id']


def _hotels_in_region(region_id):
    return [x['id'] for x in
            json.load(urllib2.urlopen(config['end_point']['hotels_in_region'] + str(region_id)))['hotelIDs']]


def save_hotel_images(region_name, image_type='thumbnail'):
    region_id = _resolve_region(region_name)
    hotel_ids = _hotels_in_region(region_id)
    for hotel_id in hotel_ids:
        logging.info("loading image of hotel: " + hotel_id)
        save_hotel_images_parallel(hotel_id, image_type)


if __name__ == '__main__':
    save_hotel_images('Indianapolis', 'large1000')
