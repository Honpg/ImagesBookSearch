from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import urllib.request
import os
import re


# Define a Scrapy spider class for crawling and scraping book data
class SipSpider(CrawlSpider):
    # Name of the spider
    name = "spibook"
    # Allowed domain for crawling
    allowed_domains = ["fahasa.com"]
    # List of URLs to start crawling from
    start_urls = []

    # Book categories to scrape
    types = [
        "tam-ly-ky-nang-song",
        "kinh-te-chinh-tri-phap-ly",
        "khoa-hoc-ky-thuat",
        "nu-cong-gia-chanh",
        "van-hoa-nghe-thuat-du-lich",
        "thieu-nhi",
        "tu-dien",
    ]

    # Generate the `start_urls` dynamically based on categories and pages
    for type in types:
        for page in range(1, 31):  # Crawl up to 29 pages per category
            start_urls.append(
                f"https://www.fahasa.com/sach-trong-nuoc/{type}.html?order=num_orders&limit=24&p={page}"
            )

    # Define rules to follow links and extract data
    rules = [
        # Extract links to individual product pages and call `parse_item` to process them
        Rule(
            LinkExtractor(
                restrict_css="div.category-products.row div.product.images-container a"
            ),
            callback="parse_item",
            follow=True,
        ),
    ]

    # Callback function to process each product page
    def parse_item(self, response):
        # Extract the name of the book
        name = self.get_name(response)
        # Extract the book's genre from the breadcrumb navigation
        genre = response.css("div.container-inner.breadcrumbs a::text").getall()[1]
        # Extract the image URL of the book
        image_url = self.get_image_url(response)
        price = self.get_price(response)

        # Skip items missing crucial fields
        if not name or not image_url:
            self.logger.warning(
                f"Skipping item due to missing name or image: {response.url}"
            )
            return
        
        # If an image URL is available, download the image and save the local path
        if image_url:
            image_path = self.download_image(image_url, genre)


        # Create an item dictionary with the extracted data
        item = {    
            "image path": image_path,
            "title": name,
            "price": price,
            "image url": image_url,
        }

        # Yield the item to store or process further
        yield item

    # Helper function to extract the book's name
    def get_name(self, response):
        # Extract potential names from the product title
        names = response.css("h1.fhs_name_product_desktop::text").getall()
        # Clean and filter meaningful names
        clean_names = [name.strip() for name in names if name.strip()]
        if clean_names:  # Return the first valid name
            clean_name = clean_names[0]
            # Exclude items like "Combo" or "Bộ" from the product name
            if not re.search("^Combo", clean_name) and not re.search("^Bộ", clean_name):
                return clean_name
            
    # Helper function to extract the author's name(s)
    def get_author(self, response):
        # Extract the author's name
        author = response.css(
            "div.product-view-sa-author span:nth-of-type(2)::text"
        ).get()
        # Clean up extra whitespace
        author = re.sub(r"\s+", " ", author).strip()

        # Handle multiple authors by splitting on commas
        if re.search(",", author):
            author = author.split(", ")  # Split authors into a list
        return author
    

    def get_price(self,response):
        price = response.css('div.price-box p.special-price span.price::text').get().strip().replace('\xa0','')
        return price


    # Helper function to extract the image URL
    def get_image_url(self, response):
        # Extract the URL of the main product image
        image_url = response.css(
            "div.product-essential-media div.product-view-image-product.fhs_img_frame_container img::attr(data-src)"
        ).get()
        return image_url
    
    

    # Helper function to download the image
    def download_image(self, image_url, genre):
        # Define folder paths for saving images
        folder_path = (
            f"./books/{genre}/"  # Genre-specific folder
        )
        folder_path_all = (
            "./bookss/"  # General folder for all images
        )

        if image_url:
            # Generate a valid image filename from the URL
            image_name = os.path.basename(image_url)

            # Create the genre-specific folder if it doesn't exist
            if os.path.exists(folder_path):
                save_path = os.path.join(folder_path, image_name)
            else:
                os.makedirs(folder_path)
                save_path = os.path.join(folder_path, image_name)

            # Save the image in the general folder
            save_path_all = os.path.join(folder_path_all, image_name)

            # Download the image from the URL
            try:
                urllib.request.urlretrieve(
                    image_url, save_path
                )  # Save to genre-specific folder
                urllib.request.urlretrieve(
                    image_url, save_path_all
                )  # Save to general folder
                self.logger.info(f"Image saved: {image_name}")
            except Exception as e:
                self.logger.error(f"Failed to download image {image_name}: {e}")

        return save_path
