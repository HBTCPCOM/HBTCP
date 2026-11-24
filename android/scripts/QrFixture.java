import com.google.zxing.BarcodeFormat;
import com.google.zxing.qrcode.QRCodeWriter;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;

/** Generates a local synthetic QR image for the emulator camera; never contains user credentials. */
public final class QrFixture {
    public static void main(String[] args) throws Exception {
        var matrix = new QRCodeWriter().encode(args[0], BarcodeFormat.QR_CODE, 768, 768);
        var image = new BufferedImage(768, 768, BufferedImage.TYPE_INT_RGB);
        for (int y = 0; y < 768; y++) {
            for (int x = 0; x < 768; x++) image.setRGB(x, y, matrix.get(x, y) ? 0x080603 : 0xFCF7EE);
        }
        ImageIO.write(image, "PNG", new File(args[1]));
    }
}
