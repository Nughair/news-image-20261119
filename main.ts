// main.ts — news-image-20261119 entrypoint (Node 22, standard library only).
// Copies the pre-rendered entry.png beside this file to $MAKEFUN_OUTPUT_DIR
// (default /output) as entry.png, validating its magic bytes and size.
import { copyFileSync, readFileSync, statSync, mkdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const dest = join(outDir, "entry.png");

const buf = readFileSync(src);
const isPng = buf.length >= 8 &&
  buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47 &&
  buf[4] === 0x0d && buf[5] === 0x0a && buf[6] === 0x1a && buf[7] === 0x0a;
const isJpeg = buf.length >= 3 && buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff;
if (!isPng && !isJpeg) {
  throw new Error("entry.png is neither a PNG nor a JPEG (bad magic bytes)");
}
if (buf.length > 1048576) {
  throw new Error("entry.png is " + buf.length + " bytes, over the 1048576 limit");
}

if (!existsSync(outDir)) {
  mkdirSync(outDir, { recursive: true });
}
copyFileSync(src, dest);
const written = statSync(dest).size;
console.log("wrote " + dest + " " + written + " bytes");
