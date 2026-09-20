#!/bin/sh
# Publish the site. Run after committing changes on main.
#   ./deploy.sh          -> pushes to GitHub and deploys to AWS (S3 + CloudFront) = venkayaswamy.com
set -e
cd "$(dirname "$0")"
BUCKET=venkayaswamy-site-030011113848
DIST=E1H9ES2VPQGWUO

# restamp asset links so browsers fetch fresh CSS/JS after every deploy
STAMP=$(date +%s)
sed -i '' -E "s/(\.(css|js))\?v=[0-9]+/\1?v=$STAMP/g" www/*.html www/admin/*.html
git add www/*.html www/admin/*.html && git -c user.name="deploy" -c user.email="deploy@srivenkaiahswamy.com" commit -q -m "deploy $STAMP" || true
git push origin main

echo "Uploading www/ to S3..."
# Pages, scripts and styles: browsers must revalidate (short max-age). Images/fonts: cache for a day.
aws s3 sync www/ "s3://$BUCKET/" --delete --exclude ".DS_Store" --exclude "*" --include "*.html" --include "*.js" --include "*.css" --include "*.json" --include "*.webmanifest" --include "*.xml" --include "*.txt" \
  --cache-control "max-age=60, must-revalidate"
aws s3 sync www/ "s3://$BUCKET/" --delete --exclude ".DS_Store" --exclude "*.html" --exclude "*.js" --exclude "*.css" --exclude "*.json" --exclude "*.webmanifest" --exclude "*.xml" --exclude "*.txt" \
  --cache-control "max-age=86400"
# The service worker must never be cached
aws s3 cp www/sw.js "s3://$BUCKET/sw.js" --cache-control "no-cache" --content-type "application/javascript"

echo "Clearing CloudFront cache..."
aws cloudfront create-invalidation --distribution-id "$DIST" --paths "/*" --query Invalidation.Id --output text
echo "Deployed. Live on https://srivenkaiahswamy.com in a minute or two."
