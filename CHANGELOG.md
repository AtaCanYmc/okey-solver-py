# Changelog

## [0.4.0](https://github.com/AtaCanYmc/okey-solver-py/compare/v0.3.0...v0.4.0) (2026-07-17)


### Features

* add asynchronous frame analysis to VisionSolverEngine and Orchestrator ([32842f9](https://github.com/AtaCanYmc/okey-solver-py/commit/32842f9a662dd5b573f92efec9b08d61d90a8f82))
* add FastAPI microservice for Okey solver with CLI support and vision integration ([4740cc3](https://github.com/AtaCanYmc/okey-solver-py/commit/4740cc39f3b70a65b785a3ecb7cb44115841a984))
* add GitHub token to release workflow for improved access ([0d79f42](https://github.com/AtaCanYmc/okey-solver-py/commit/0d79f4272392a9ba22a4caa203918ab0e0941e58))
* add integration tests for vision pipeline with mock data handling ([743514b](https://github.com/AtaCanYmc/okey-solver-py/commit/743514b33f9e7c0e91cfe5988072443a8aff4341))
* add lazy loading for optional dependencies and improve error handling in frame adapters ([151773a](https://github.com/AtaCanYmc/okey-solver-py/commit/151773a0e9a22a4963465b7079c1c5bc446f13d8))
* add local YOLO and Roboflow providers for tile detection, enhance .gitignore, and update tests ([5fadc99](https://github.com/AtaCanYmc/okey-solver-py/commit/5fadc99c0d4ce12cd335016315d2efff6a3d4a9d))
* add python-multipart as an optional dependency for server extras in poetry.lock ([42be79e](https://github.com/AtaCanYmc/okey-solver-py/commit/42be79ed02376be40782c5a1127422ffa9ccea81))
* add python-multipart dependency to server extras in pyproject.toml ([4cf1b25](https://github.com/AtaCanYmc/okey-solver-py/commit/4cf1b253b0df312902036bad25375a05ddcae794))
* add Roboflow workflow types for image size and predictions ([fd9d8eb](https://github.com/AtaCanYmc/okey-solver-py/commit/fd9d8eb1d19813e3d7291d054dae5093b9675668))
* add RoboflowWorkflowLabelVisualization class and update container model to include label visualization output ([ef8bd4a](https://github.com/AtaCanYmc/okey-solver-py/commit/ef8bd4a74c944a52a0668ae42b2f748826f8f3d2))
* add RoboflowWorkflowProvider for tile detection using Roboflow Inference SDK ([d18e592](https://github.com/AtaCanYmc/okey-solver-py/commit/d18e5925c72373f4495dbd88c227bf57d23a96a8))
* add solver factory functions for standard and Okey 101 solvers ([6758679](https://github.com/AtaCanYmc/okey-solver-py/commit/6758679e12cdabbf609f3080c5bfecb903172fac))
* add vision extraction endpoints for local and Roboflow models with corresponding tests ([99a621b](https://github.com/AtaCanYmc/okey-solver-py/commit/99a621b28f08307108a96ae0d487c2d0a8cba96b))
* add workspace name parameter to RoboflowProvider and update model ID handling ([9313d6f](https://github.com/AtaCanYmc/okey-solver-py/commit/9313d6f7d491844cfbbc906040a609b2861f1b9d))
* add workspace parameter to API endpoints for Roboflow integration ([bb8e1b9](https://github.com/AtaCanYmc/okey-solver-py/commit/bb8e1b906acc9d25115f41715f993db669e8732c))
* enhance backtracking solver with memoization and improve async processing in vision pipeline ([addbee7](https://github.com/AtaCanYmc/okey-solver-py/commit/addbee76053251d819119298e61cf333562d6d42))
* enhance orchestrator with new result types and improve tile parsing strategy ([c6e9afe](https://github.com/AtaCanYmc/okey-solver-py/commit/c6e9afe9fd49de3f97f3833f8e5e09e9432d6d0b))
* enhance prediction extraction logic and add new test cases for Roboflow API requests ([bf87c54](https://github.com/AtaCanYmc/okey-solver-py/commit/bf87c549148b004e99576717698541ef87a39d2d))
* enhance README with logo and improved formatting for better pre… ([340dfaa](https://github.com/AtaCanYmc/okey-solver-py/commit/340dfaa2851837c3a616a9ce6796588eaf4b2a76))
* enhance README with logo and improved formatting for better presentation ([370c18a](https://github.com/AtaCanYmc/okey-solver-py/commit/370c18ab6b69b856c99d191b05aa07fa6d4c76dd))
* enhance README with modular architecture details, installation instructions, and CLI commands ([975bd93](https://github.com/AtaCanYmc/okey-solver-py/commit/975bd93d7099ee236268e734b1b4e3d42400045c))
* enhance type annotations and improve CI configuration for better testing and error handling ([67e98a1](https://github.com/AtaCanYmc/okey-solver-py/commit/67e98a1a32c882777d7e2b63f0d40dc03912d642))
* enhance vision processing with dynamic pipeline selection and environment loading ([6716dc1](https://github.com/AtaCanYmc/okey-solver-py/commit/6716dc1f4ae829f462c1f2f44ad69c6ce6041a89))
* enhance VisionSolverEngine and Orchestrator with strategy selection and solver injection ([58e64db](https://github.com/AtaCanYmc/okey-solver-py/commit/58e64db1359bdb1d56fe0c5f33219589d5377c5f))
* implement dependency injection for solver engine and vision pipeline ([7a3d589](https://github.com/AtaCanYmc/okey-solver-py/commit/7a3d589e60c5ba92bd8dceac72548f7d76b42c9f))
* implement error handling improvements and logging for Roboflow provider ([b21f0c6](https://github.com/AtaCanYmc/okey-solver-py/commit/b21f0c6d1e2c97671dd2ec9707e55896554243eb))
* implement greedy solver strategy for optimal tile arrangement ([2f537e6](https://github.com/AtaCanYmc/okey-solver-py/commit/2f537e6e6e0b572405bf71636c28da3c20966144))
* implement logging and refactor vision provider initialization in app and routers ([e423dc3](https://github.com/AtaCanYmc/okey-solver-py/commit/e423dc3d7d3d60c840d3bab052a60ba1e6f7e82c))
* improve code formatting and consistency across multiple files ([638e4b0](https://github.com/AtaCanYmc/okey-solver-py/commit/638e4b031a4813b3cfced61d935b852308f49eb0))
* improve logging formatting in app.py and __init__.py ([7a1a8a7](https://github.com/AtaCanYmc/okey-solver-py/commit/7a1a8a7c31038da5471749b87ff28e6f7e50df8d))
* introduce okey_orchestrator module with VisionOrchestrator and VisionSolverEngine ([fa72b81](https://github.com/AtaCanYmc/okey-solver-py/commit/fa72b8102ee460e9d1df8a9d94a4996d2ef7da6e))
* refactor app structure by moving endpoints to routers and adding health check ([96e93a5](https://github.com/AtaCanYmc/okey-solver-py/commit/96e93a5a1ae50b9893a216c2e22f8db5b34be3eb))
* refactor configuration handling to use state module instead of environment variables ([df941ce](https://github.com/AtaCanYmc/okey-solver-py/commit/df941ce2045d06458812163660c6523a1707a27b))
* refactor constructor parameters for Roboflow workflow class ([1c35456](https://github.com/AtaCanYmc/okey-solver-py/commit/1c35456c34ddfdabda7c771369ddba5c849e27bc))
* refactor imports and clean up code formatting across multiple f… ([c1db192](https://github.com/AtaCanYmc/okey-solver-py/commit/c1db1928454839f2f03413e4b67d15cdd2006da9))
* refactor imports and clean up code formatting across multiple files ([4cedbfc](https://github.com/AtaCanYmc/okey-solver-py/commit/4cedbfc6a86c688efd2588d142b9ffe64e27acf6))
* refactor RoboflowProvider to use Inference SDK and improve model ID handling ([1fc86b9](https://github.com/AtaCanYmc/okey-solver-py/commit/1fc86b9b1bbd8725251cadd9456ec6cc61d5983e))
* refactor RoboflowProvider to use Roboflow Python SDK and improve model loading ([cce9c38](https://github.com/AtaCanYmc/okey-solver-py/commit/cce9c38c0be8aec419079687b3893cfecc1f4a90))
* refactor types and error handling by introducing okey_core module ([e920962](https://github.com/AtaCanYmc/okey-solver-py/commit/e920962ae4fb71d10e36737a41c92055b75cb6f4))
* refactor vision endpoint parameters for improved readability and consistency ([438bd9a](https://github.com/AtaCanYmc/okey-solver-py/commit/438bd9ad7897ccd58f8a0133ee305eebc85fce91))
* refactor vision provider integration by removing LocalYoloProvider and RoboflowProvider, and updating endpoints to use RoboflowWorkflowProvider ([4ab024b](https://github.com/AtaCanYmc/okey-solver-py/commit/4ab024b0e003113926e9503799fe6eef3c214ec4))
* remove caching for Poetry in CI and release workflows to streamline dependency installation ([6a5dfca](https://github.com/AtaCanYmc/okey-solver-py/commit/6a5dfca055966d117ddb84cc4a72c3a2235ee5f3))
* reorganize logging setup and update imports in core modules ([018db62](https://github.com/AtaCanYmc/okey-solver-py/commit/018db620bfe9018bac3911b09d9afdbb50f721f1))
* restrict torch and torchvision versions in pyproject.toml ([414b4d1](https://github.com/AtaCanYmc/okey-solver-py/commit/414b4d12b07b319e54927eb9f3d4c62eecb681d3))
* train notebook ([7de68e5](https://github.com/AtaCanYmc/okey-solver-py/commit/7de68e55c9bb148dd8706eea42d53edd15a7c734))
* update architecture and README to include new model providers for object detection ([14fdca8](https://github.com/AtaCanYmc/okey-solver-py/commit/14fdca8016065824f868fd3a9b07551c297e976f))
* update architecture documentation and add contributing guidelines ([ce4c021](https://github.com/AtaCanYmc/okey-solver-py/commit/ce4c021a1589d748828b06cdc075a3dd2856d4c2))
* update default model ID to version 3 in RoboflowProvider initialization ([cb4d19d](https://github.com/AtaCanYmc/okey-solver-py/commit/cb4d19da2d78792a2236e6d7477ea91ebe00a798))
* update fastapi and add starlette version constraints for compat… ([8cc8312](https://github.com/AtaCanYmc/okey-solver-py/commit/8cc8312cac90205ff68528852f2107faf0bc01e4))
* update fastapi and add starlette version constraints for compatibility ([aabd918](https://github.com/AtaCanYmc/okey-solver-py/commit/aabd918b025fdfebca68d1c3137b17d8e6597ada))
* update model ID construction in detect method to align with Inference SDK validation format ([162f813](https://github.com/AtaCanYmc/okey-solver-py/commit/162f813af708ff84c1ac19c7a4668f00846dc7b9))
* update model ID in vision extraction endpoints and improve parameter formatting for consistency ([0ade992](https://github.com/AtaCanYmc/okey-solver-py/commit/0ade992131e98765278095c7dbc964926dff04b3))
* update poetry.lock to include new packages and adjust optional dependencies for server and vision extras ([f5c419a](https://github.com/AtaCanYmc/okey-solver-py/commit/f5c419ab2a1fb32117f3b642aa92aee0a8466e9d))
* update Python version constraint and enhance README with capability matrix and system flow diagram ([917dca1](https://github.com/AtaCanYmc/okey-solver-py/commit/917dca11e3f362310832c69095f1643a6acc9323))
* update README to include strategy selection details for okey_orchestrator ([7d68be6](https://github.com/AtaCanYmc/okey-solver-py/commit/7d68be67f019a83f3d720e5824b41ac1450c4c65))
* update README with details on pretrained Okey-Rummikub model and Kaggle dataset ([75231a4](https://github.com/AtaCanYmc/okey-solver-py/commit/75231a42a5f36bea69736ff05e790732c61289c8))
* update release action to use googleapis/release-please-action ([af3b6d7](https://github.com/AtaCanYmc/okey-solver-py/commit/af3b6d7bc549c44f09bc92a966cc9f1c8c76a3de))
* update release action to use googleapis/release-please-action ([25ff19a](https://github.com/AtaCanYmc/okey-solver-py/commit/25ff19a935fdb43a0b0be6fa43b323e227d7cbd8))
* update release workflow to use newer actions and streamline Poetry installation ([6165308](https://github.com/AtaCanYmc/okey-solver-py/commit/61653087d8835b6e4a3122f7b7c35c6e515a040c))
* update roboflow dependency to version 1.3.13 in pyproject.toml ([e837a09](https://github.com/AtaCanYmc/okey-solver-py/commit/e837a09b7646042d5fa7a1afc1cd1cda7e26e4f4))
* update torch and torchvision version constraints for platform compatibility ([93a03c9](https://github.com/AtaCanYmc/okey-solver-py/commit/93a03c93510522396321ba425cd4e05d0c779181))
* update vision extraction endpoints to return raw response data and refactor response model ([1111c3a](https://github.com/AtaCanYmc/okey-solver-py/commit/1111c3a16b849e4f9d6a2f300352f05d6b16c1db))
* update vision processing endpoints to support local and Roboflow models with enhanced error handling ([a8b296e](https://github.com/AtaCanYmc/okey-solver-py/commit/a8b296e5972a5c067047667b011651ff78ebecb5))
* update workflow ID and add api_url parameter to Roboflow workflow provider ([b7127d7](https://github.com/AtaCanYmc/okey-solver-py/commit/b7127d705bc3f873e686f3175c7949620c90ab67))
* use getattr to safely access boxes attribute in local_yolo.py ([16c3001](https://github.com/AtaCanYmc/okey-solver-py/commit/16c30013ba0f45cbc7e7fef3e1894e059b85725a))

## [0.3.0](https://github.com/AtaCanYmc/okey-solver-py/compare/v0.2.0...v0.3.0) (2026-07-04)


### Features

* add README.md reference in pyproject.toml ([af52966](https://github.com/AtaCanYmc/okey-solver-py/commit/af52966189a10a7c4c1ed4f2e3d24a3c456a33fe))

## [0.2.0](https://github.com/AtaCanYmc/okey-solver-py/compare/v0.1.1...v0.2.0) (2026-07-04)


### Features

* add run configuration for Telegram bot in project setup ([17f3310](https://github.com/AtaCanYmc/okey-solver-py/commit/17f33108c9fb37961dd0778504f85e470e0e11b5))
* add Telegram bot for Okey Vision with image processing and layout solving ([530a761](https://github.com/AtaCanYmc/okey-solver-py/commit/530a7613868177817f705b9cc7e93248bbe2c7eb))


### Bug Fixes

* improve bot initialization and error handling for missing TELEGRAM_BOT_TOKEN ([6def8c8](https://github.com/AtaCanYmc/okey-solver-py/commit/6def8c8ca59c5ad37d47358bdca94d296629c52c))
* update release workflow to include OIDC permissions and improve PyPI publishing steps ([0f44ca2](https://github.com/AtaCanYmc/okey-solver-py/commit/0f44ca2312e64b21947e7ef814c6fa082576a176))

## [0.1.1](https://github.com/AtaCanYmc/okey-solver-py/compare/v0.1.0...v0.1.1) (2026-07-04)


### Bug Fixes

* update poetry install command to include all extras ([4be6025](https://github.com/AtaCanYmc/okey-solver-py/commit/4be6025e9b9ec7b71c87433eba50b49872186178))

## 0.1.0 (2026-07-04)


### Features

* add CLI tools for Okey Solver and Okey Vision with usage documentation ([e7fe7b7](https://github.com/AtaCanYmc/okey-solver-py/commit/e7fe7b7e8d4c0084ca9f7df131e063e056bc9229))
* add initial implementation of okey_solver and okey_vision modules ([203c28a](https://github.com/AtaCanYmc/okey-solver-py/commit/203c28a270c341692dae87a550357daec7f27e9e))


### Bug Fixes

* update paths in CI configuration for Ruff linter and formatter checks ([cbf5f37](https://github.com/AtaCanYmc/okey-solver-py/commit/cbf5f37f30371721e65e8384a7df14b415e40c53))
