#!/usr/bin/env sh
# adapted from https://gist.github.com/imkh/1e349de95879d22445550f3ac222fc0f

if [ -z "$1" ]; then
  DIRECTORY="."
else
  DIRECTORY="$1"
fi

echo "🔄 Looking for image files in \"$DIRECTORY\""

find "$DIRECTORY" -type f -print0 | xargs -0 file --mime-type | grep -F 'image/' | cut -d ':' -f 1 | while read -r FILE_PATH; do
  dimensions=$(magick identify -format '%wx%h' "$FILE_PATH" 2>/dev/null)
  if [ $? -ne 0 ]; then
    echo "⚠️  Error identifying $FILE_PATH"
    continue
  fi

  width=$(echo "$dimensions" | cut -d'x' -f1)
  height=$(echo "$dimensions" | cut -d'x' -f2)

  if [ "$width" -gt "$height" ]; then # landscape
      FILE_NAME="${FILE_PATH%.*}"
      FILE_EXTENSION="${FILE_PATH##*.}"
      OUTPUT="${FILE_NAME}_%d.${FILE_EXTENSION}"

      magick identify -format "%[input] %[magick] %[width]x%[height] %[bit-depth]-bit %[colorspace]\n" "$FILE_PATH" 2>/dev/null

      if [ $? -ne 0 ]; then
        echo "⚠️  Error identifying $FILE_PATH"
        continue
      fi

      magick "$FILE_PATH" -crop 2x1@ -reverse +repage "$OUTPUT"
      if [ $? -eq 0 ]; then
        rm "$FILE_PATH"
      else
        echo "⚠️  Error processing $FILE_PATH"
      fi
  fi
done

echo "✅ Done!"
