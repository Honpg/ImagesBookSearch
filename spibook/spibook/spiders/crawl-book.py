from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import urllib.request 
import os

class SipSpider(CrawlSpider):
     name = 'spibook'
     allowed_domains = ['fahasa.com']
     start_urls = []

     types = ["tam-ly-ky-nang-song", "kinh-te-chinh-tri-phap-ly", "khoa-hoc-ky-thuat"]
     for type in types:
          for page in range(1, 5):
               start_urls.append(f"https://www.fahasa.com/sach-trong-nuoc/{type}.html?order=num_orders&limit=24&p={page}")

     rules = [
          Rule(LinkExtractor(restrict_css="div.category-products.row div.product.images-container a"), callback='parse_item', follow=True),
     ]

     def parse_item(self, response):
          name = self.get_name(response)
          genre = response.css('div.container-inner.breadcrumbs a::text').getall()[1]
          image_url = self.get_image_url(response)
          

          if not name or not image_url:
               self.logger.warning(f"Skipping item due to missing name or image: {response.url}")
               return  

          item = {
               'name': name,
               'genre': genre,
               'image_URL': image_url
          }
          
          if image_url:
               item['image_local_path'] = self.download_image(image_url, genre)

          yield item


     def get_name(self, response):
          names = response.css('h1.fhs_name_product_desktop::text').getall()
          clean_names = [name.strip() for name in names if name.strip()]
          if clean_names:  # Return the first meaningful name
               return clean_names[0]
          
     
     def get_image_url(self, response):
          # Extract the first image URL from the product page (assuming the image is inside <img>)
          image_url = response.css("div.product-essential-media div.product-view-image-product.fhs_img_frame_container img::attr(data-src)").get()
          return image_url


     def download_image(self, image_url, gerne):
          folder_path = f"./project/books/{gerne}/"
     
          if image_url:
               # Create a valid filename from the product name (remove invalid characters)
               image_name = os.path.basename(image_url)

               # Create a folder to save the image based on the book's gerne
               if os.path.exists(folder_path):
                    save_path = os.path.join(folder_path, image_name)
               else:
                    os.makedirs(folder_path)
                    save_path = os.path.join(folder_path, image_name)

               # Download the image and save it
               try:
                    urllib.request.urlretrieve(image_url, save_path)
                    self.logger.info(f"Image saved: {image_name}")
               except Exception as e:
                    self.logger.error(f"Failed to download image {image_name}: {e}")
               finally:
                    return save_path

          
