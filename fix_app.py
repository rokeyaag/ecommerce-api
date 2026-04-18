import re

with open('frontend/src/App.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all question mark sequences (emoji placeholders)
# but preserve valid JS operators like ?., ??, ===, etc.
content = content.replace("'????'", "''")
content = content.replace('"????"', '""')
content = content.replace("'??????'", "''")
content = content.replace("'???????"  , "''")
content = content.replace("'???'", "''")
content = content.replace("'??'", "''")
content = content.replace("Orders over ???1000", "Orders over 1000 BDT")
content = content.replace("???? EXCLUSIVE DEAL", "EXCLUSIVE DEAL")
content = content.replace("Shop Now ???", "Shop Now")
content = content.replace("Add to Cart", "Add to Cart")

# Fix carousel filter - use final_image
content = content.replace(
    "const slides = products.filter(p => p.image)",
    "const slides = products.filter(p => p.image || p.image_url || p.final_image)"
)

# Fix getImg to use final_image
content = content.replace(
    "const getImg = (image) => {",
    "const getImg = (image, image_url) => {\n  if (image_url) return image_url;"
)
content = content.replace("getImg(p.image)", "getImg(p.image, p.final_image || p.image_url)")
content = content.replace("getImg(product.image)", "getImg(product.image, product.final_image || product.image_url)")

with open('frontend/src/App.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')