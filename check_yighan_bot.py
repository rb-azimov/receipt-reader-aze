import traceback

from dotenv import load_dotenv
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageEnhance
from pyzbar.pyzbar import decode
import io
from src.low_level_processors.application_properties_builder import ApplicationPropertiesBuilder
from src.low_level_processors.application_properties_service import ApplicationPropertiesService
from src.low_level_processors.receipt_service import ReceiptService


# Function to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("<b>ÇekYığan işləyir!</b>", parse_mode="HTML")
    await update.message.reply_text("<i>Qəbzdəki QR kod hissəsinin şəklini göndərin.</i>", parse_mode="HTML")



# Function to handle incoming QR code images
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Şəkil yüklənilmədi. Təkrar sınayın, zəhmət olmasa.")
        return

    try:
        # Get the photo file
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        # Open the image from bytes
        image = Image.open(io.BytesIO(photo_bytes))

        # Convert to grayscale
        grayscale_image = image.convert("L")

        # Enhance contrast (optional)
        enhancer = ImageEnhance.Contrast(grayscale_image)
        enhanced_image = enhancer.enhance(2.0)

        image = enhanced_image

        # Decode the QR code
        decoded_objects = decode(image)

        if decoded_objects:
            for obj in decoded_objects:
                decoded_text = obj.data.decode('utf-8')
                await update.message.reply_text(f"QR kodun məzmunu: {decoded_text}")
                application_properties = ApplicationPropertiesBuilder.prepare_application_properties_v_core_1_logic_0_depend_1(is_debug_on=True)
                ApplicationPropertiesService.load_properties(application_properties)
                receipt_service = ReceiptService()
                try:
                    fiscal_code = decoded_text.split('=')[-1]
                    receipt = receipt_service.mine_receipt(fiscal_code=fiscal_code)
                    receipt._fiscal_code = fiscal_code
                except Exception as e:
                    print(f"Error occured: {e}")
                    await update.message.reply_text(f"Qəbzin oxunması baş vermədi: {e}.")
                    traceback.print_exc()
                else:
                    print(receipt.__str__())
                await update.message.reply_text(receipt.__str__())

        else:
            await update.message.reply_text("QR kod oxunmur!")
    except Exception as e:
        await update.message.reply_text(f"Qeyri-müəyyən səbəbdən proqram işləmir.: {str(e)}")
    await start(update, context)

# Main function to set up the bot
def main():
    # Replace 'YOUR_TOKEN_HERE' with your Telegram bot token
    load_dotenv(dotenv_path='.env')
    bot_token = os.getenv('TELEGRAM_BOT_KEY')
    if not bot_token:
        print("Error: API_KEY environment variable is not set.")
        return

    application = Application.builder().token(bot_token).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))

    # Message handler for images
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
