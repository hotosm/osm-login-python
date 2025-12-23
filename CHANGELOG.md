# Changelog

## 2.1.0 (2025-12-23)

### Fix

- pydantic model_dump syntax removed

## 2.0.0 (2024-08-09)

### Feat

- return the raw OSM OAuth2 token in addition (to use or discard as required)

### Fix

- strip trailing slash if included in osm_url
- update pydantic deprecated use of .json() --> .model_dump_json()

### Refactor

- move serialization logic into a reusable private method
- tweak API to return `user_data` and `oauth_token` params
- also serialise the raw_token in response

## 1.0.3 (2024-04-10)

### Fix

- replace pydantic ValidationError with ValueError

## 1.0.2 (2023-12-05)

- pin all dependencies >= over ~=

## 1.0.1 (2023-09-28)

### Refactor

- update gitignore files

## 1.0.0 (2023-09-02)
