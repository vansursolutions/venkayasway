#!/bin/sh
# Publish the site. Run after committing changes on main.
#   ./deploy.sh          -> pushes to GitHub and deploys to AWS (S3 + CloudFront) = venkayaswamy.com
set -e
cd "$(dirname "$0")"
BUCKET=venkayaswamy-site-030011113848
DIST=E1H9ES2VPQGWUO

git push origin main

echo "Uploading www/ to S3..."
aws s3 sync www/ "s3://$BUCKET/" --delete --exclude ".DS_Store"
# The service worker must never be cached by the CDN/browser for long
aws s3 cp www/sw.js "s3://$BUCKET/sw.js" --cache-control "no-cache" --content-type "application/javascript"

echo "Clearing CloudFront cache..."
aws cloudfront create-invalidation --distribution-id "$DIST" --paths "/*" --query Invalidation.Id --output text
echo "Deployed. Live on https://venkayaswamy.com in a minute or two."
