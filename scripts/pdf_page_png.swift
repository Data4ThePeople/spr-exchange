// Render one page of a PDF to a PNG, to check a scanned page by eye.
//   swift scripts/pdf_page_png.swift <in.pdf> <page> <out.png> [dots per inch, default 150]
import Foundation
import PDFKit
import ImageIO
import UniformTypeIdentifiers

let a = CommandLine.arguments
guard a.count >= 4, let doc = PDFDocument(url: URL(fileURLWithPath: a[1])), let n = Int(a[2]), let page = doc.page(at: n - 1) else {
    FileHandle.standardError.write("usage: pdf_page_png.swift in.pdf page out.png [dpi]\n".data(using: .utf8)!)
    exit(1)
}
let scale = CGFloat(a.count > 4 ? Double(a[4])! : 150.0) / 72.0
let box = page.bounds(for: .mediaBox)
let w = Int(box.width * scale), h = Int(box.height * scale)
let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpaceCreateDeviceRGB(),
                    bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
ctx.scaleBy(x: scale, y: scale)
page.draw(with: .mediaBox, to: ctx)
let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: a[3]) as CFURL, UTType.png.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(dest, ctx.makeImage()!, nil)
CGImageDestinationFinalize(dest)
