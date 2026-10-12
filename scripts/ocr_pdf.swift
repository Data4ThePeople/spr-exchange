// Read the text of every page of a PDF with macOS's built-in text recognition.
// Used for scanned government documents that have no text layer.
//   swift scripts/ocr_pdf.swift <in.pdf> <out.txt> [first page] [last page]
// Compile once for long files: swiftc -O scripts/ocr_pdf.swift -o scratch/ocr_pdf
// Each page is rendered at 200 dots per inch and written under a "=== page N ===" line.
import Foundation
import PDFKit
import Vision

let args = CommandLine.arguments
guard args.count >= 3, let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
    FileHandle.standardError.write("usage: ocr_pdf.swift in.pdf out.txt\n".data(using: .utf8)!)
    exit(1)
}
var out = ""
let first = args.count > 3 ? Int(args[3])! - 1 : 0
let last = args.count > 4 ? min(Int(args[4])!, doc.pageCount) : doc.pageCount
for i in first..<last {
    guard let page = doc.page(at: i) else { continue }
    let box = page.bounds(for: .mediaBox)
    let scale: CGFloat = 200.0 / 72.0
    let w = Int(box.width * scale), h = Int(box.height * scale)
    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
                              space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { continue }
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: ctx)
    guard let img = ctx.makeImage() else { continue }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = true
    try? VNImageRequestHandler(cgImage: img, options: [:]).perform([req])
    let lines = (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }
    out += "=== page \(i + 1) ===\n" + lines.joined(separator: "\n") + "\n"
}
try! out.write(toFile: args[2], atomically: true, encoding: .utf8)
print("\(args[1].split(separator: "/").last ?? ""): \(doc.pageCount) pages")
