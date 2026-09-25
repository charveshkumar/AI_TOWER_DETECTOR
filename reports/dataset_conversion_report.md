# Phase 2 Dataset Conversion & Dry-Run Report

**Project**: AI-Based Tower Component Detection System  
**Source Directory**: `A:\Electrohack\data\processed\roboflow_export`  
**Target Output Directory**: `C:\Users\Raghavendra\AppData\Local\Temp\tmpdvdcb5hy\yolo_test_out`  
**Execution Mode**: `DRY RUN (Read-Only Validation)`  

---

## 1. Dynamic Class Remapping Verification

| Source Class Name (Export) | Source Export ID | Target Class Name (System Standard) | Target Class ID | Remapped Total Objects |
| :--- | :--- | :--- | :--- | :--- |
| `monopole_tower` | `0` | `monopole_tower` | `1` | **36 instances** |
| `supporting_tower` | `1` | `supporting_tower` | `0` | **91 instances** |

## 2. Polygon to Bounding Box Normalization

- **Converted Polygon Files**: `1` file containing **8 polygon instances**.
  - File: `img_00eeee4fc7754a82_JPG.rf.8af42aa1141ebc257467120c6b3c4ace.jpg` | Line 0 (18 vertices) -> BBox `(xc=0.212171, yc=0.142955, w=0.031433, h=0.018366)`
  - File: `img_00eeee4fc7754a82_JPG.rf.8af42aa1141ebc257467120c6b3c4ace.jpg` | Line 1 (27 vertices) -> BBox `(xc=0.220669, yc=0.342654, w=0.037098, h=0.022478)`
  - File: `img_00eeee4fc7754a82_JPG.rf.8af42aa1141ebc257467120c6b3c4ace.jpg` | Line 2 (27 vertices) -> BBox `(xc=0.663377, yc=0.247396, w=0.033626, h=0.023849)`
  - File: `img_00eeee4fc7754a82_JPG.rf.8af42aa1141ebc257467120c6b3c4ace.jpg` | Line 3 (32 vertices) -> BBox `(xc=0.572643, yc=0.124315, w=0.034174, h=0.04523)`
  - File: `img_00eeee4fc7754a82_JPG.rf.8af42aa1141ebc257467120c6b3c4ace.jpg` | Line 4 (34 vertices) -> BBox `(xc=0.57447, yc=0.166941, w=0.03527, h=0.035636)`
  - File: `img_00eeee4fc7754a82_JPG.rf.8af42aa1141ebc257467120c6b3c4ace.jpg` | Line 5 (53 vertices) -> BBox `(xc=0.290753, yc=0.183114, w=0.100512, h=0.045504)`
  - File: `img_00eeee4fc7754a82_JPG.rf.8af42aa1141ebc257467120c6b3c4ace.jpg` | Line 6 (71 vertices) -> BBox `(xc=0.658352, yc=0.17585, w=0.121162, h=0.105537)`
  - File: `img_00eeee4fc7754a82_JPG.rf.8af42aa1141ebc257467120c6b3c4ace.jpg` | Line 7 (375 vertices) -> BBox `(xc=0.431012, yc=0.405976, w=0.471674, h=0.560855)`


## 3. Grouped Split Distribution (70 / 15 / 15 Target)

| Split | Total Images | Total Objects | `supporting_tower` (Class 0) Objects | `monopole_tower` (Class 1) Objects |
| :--- | :--- | :--- | :--- | :--- |
| **Train** | `84` | `91` | 68 | 23 |
| **Val** | `18` | `18` | 9 | 9 |
| **Test** | `18` | `18` | 14 | 4 |


## 4. Discrepancy Investigation: Monopole Class Count (37 Exported vs. 25 Expected)

> [!WARNING]

> **DISCREPANCY FLAGGED**: The Roboflow source dataset contains **36 images** labeled with Class 0 (`monopole_tower`), whereas manual inspection expected **25 images** (delta of +11 images).

> This discrepancy is **NOT** silently overwritten. Below is the complete manifest of the 37 images labeled as monopole in the source export for user verification:

| # | Export Image Filename | Group / GPS ID |
| :--- | :--- | :--- |
| 01 | `img_0e7929a4069c45bd_jpg.rf.465dac252e40f6d26a38b441f0411095.jpg` | `item_img_0e7929a4069c45bd_jpg` |
| 02 | `img_0fe5d55fc0564f42_jpg.rf.f35c3c3765991b7b719cf25e28b773d6.jpg` | `item_img_0fe5d55fc0564f42_jpg` |
| 03 | `img_1025992249b44a03_jpg.rf.2f227c80b086c8b27aa5042baa6a0790.jpg` | `item_img_1025992249b44a03_jpg` |
| 04 | `img_10c04abc902c46a5_jpg.rf.7f2932cac2863c37b92f62e1337f34d2.jpg` | `item_img_10c04abc902c46a5_jpg` |
| 05 | `img_14321e8f0c474503_jpg.rf.954f1a97e0de876a9bf8b5da99dc5511.jpg` | `item_img_14321e8f0c474503_jpg` |
| 06 | `img_1a49c20eeec349b8_jpeg.rf.4576a624f68c387e3a17d684d16c202b.jpg` | `item_img_1a49c20eeec349b8_jpe` |
| 07 | `img_30b4d83fff124080_jpg.rf.cb469ac4923ea11353dc1055cf288ccd.jpg` | `item_img_30b4d83fff124080_jpg` |
| 08 | `img_379c3aa45a2e4755_jpg.rf.3b79b3927b2d5ba305adae85f172f633.jpg` | `item_img_379c3aa45a2e4755_jpg` |
| 09 | `img_396da7e485a948ea_jpg.rf.1c7f4f7cedb81291f70425b38c541c4a.jpg` | `item_img_396da7e485a948ea_jpg` |
| 10 | `img_3af8add972ce4f12_jpg.rf.7946bb1fae0b34406088009521bc81e9.jpg` | `item_img_3af8add972ce4f12_jpg` |
| 11 | `img_3b03b8d3e6244396_jpg.rf.48b7268dfac8fac1c12cfa41f44e82b7.jpg` | `item_img_3b03b8d3e6244396_jpg` |
| 12 | `img_522e9d82058144e0_jpg.rf.11a996f199c18d0b3512c30416ac1472.jpg` | `item_img_522e9d82058144e0_jpg` |
| 13 | `img_54ce663fee0143ef_jpg.rf.6974a502df4ed6b12aaa9cdd16d23844.jpg` | `item_img_54ce663fee0143ef_jpg` |
| 14 | `img_5d8939b24ca840cf_jpg.rf.aee2a563085734c2364563403afd0dc4.jpg` | `item_img_5d8939b24ca840cf_jpg` |
| 15 | `img_60420d9c58ea48c4_jpg.rf.895b4f50585f79fdcaa482c2c89ef62f.jpg` | `item_img_60420d9c58ea48c4_jpg` |
| 16 | `img_6cf28cca5ac141f1_jpg.rf.28ca6c7470a848187570231d1f776b06.jpg` | `item_img_6cf28cca5ac141f1_jpg` |
| 17 | `img_706d9612d51c4cb8_jpg.rf.2f2575a823d451e04e0e35935891a354.jpg` | `item_img_706d9612d51c4cb8_jpg` |
| 18 | `img_759864cee7794560_jpg.rf.82d4828efe5ca11c9f270eed0e58465c.jpg` | `item_img_759864cee7794560_jpg` |
| 19 | `img_838ea92de2164ded_jpg.rf.d91a30c0ddec6fd8404e91ab81a8a6ca.jpg` | `item_img_838ea92de2164ded_jpg` |
| 20 | `img_8557f04878e048e3_jpg.rf.d891a777f9405d1119364fd7b69687ed.jpg` | `item_img_8557f04878e048e3_jpg` |
| 21 | `img_8626887577af4c48_jpg.rf.097154dc0a639c2664c3efd607661eec.jpg` | `item_img_8626887577af4c48_jpg` |
| 22 | `img_8de203dea6e347ba_jpg.rf.cbc1b6a5ea4aaaf92b23de05aecce4f2.jpg` | `item_img_8de203dea6e347ba_jpg` |
| 23 | `img_a926c05ec70d42a0_jpg.rf.7509824f437f727c251fded07b3a9115.jpg` | `item_img_a926c05ec70d42a0_jpg` |
| 24 | `img_abff1cb91657419e_png.rf.0c6baafc4cd36d11f6f021d9c938c950.jpg` | `item_img_abff1cb91657419e_png` |
| 25 | `img_c1bbd1371a7f4d7c_jpg.rf.fab3eab33cb241433b3fc30f08d978d8.jpg` | `item_img_c1bbd1371a7f4d7c_jpg` |
| 26 | `img_c68ae09ce4034f44_jpg.rf.471b6d1f59d9f4e225c20be0c278563e.jpg` | `item_img_c68ae09ce4034f44_jpg` |
| 27 | `img_d1add26da12e4c85_jpg.rf.d04040934eacaf48374b991820a40124.jpg` | `item_img_d1add26da12e4c85_jpg` |
| 28 | `img_dd25675378654e39_jpg.rf.2421d6e1b8204fe785beac890531bd3a.jpg` | `item_img_dd25675378654e39_jpg` |
| 29 | `img_de01e7783ccf4d37_jpg.rf.16d52f8fdd6ab0432d8f9e9a11f72a99.jpg` | `item_img_de01e7783ccf4d37_jpg` |
| 30 | `img_f530851773d444f3_jpg.rf.06eb8f71e0c7641e35cd349a5baa9fe1.jpg` | `item_img_f530851773d444f3_jpg` |
| 31 | `img_f6f310acff4348e1_jpg.rf.0347fbd389c5b65d1449d880841f86e7.jpg` | `item_img_f6f310acff4348e1_jpg` |
| 32 | `img_f6f8dbc9f0bc4ea3_jpg.rf.441ceb21b7011489b810bcd6448a89ec.jpg` | `item_img_f6f8dbc9f0bc4ea3_jpg` |
| 33 | `img_f7a73945a186404d_jpeg.rf.de38bb598e6d4b226085d9429f072a08.jpg` | `item_img_f7a73945a186404d_jpe` |
| 34 | `img_h72ebdyu7wdwd_jpg.rf.ebad564c4f4f879338edf30c96a7d847.jpg` | `item_img_h72ebdyu7wdwd_jpg.rf` |
| 35 | `img_ha7e2u2d72db_jpg.rf.b39cf471554880fc1a212f47bc7eb954.jpg` | `item_img_ha7e2u2d72db_jpg.rf.` |
| 36 | `img_hbdy623e2u8_jpg.rf.4aea811429369510684d214cbfebf140.jpg` | `item_img_hbdy623e2u8_jpg.rf.4` |


## 5. Next Steps & Approval Gate

1. **User Review**: Review the 37 candidate monopole images above.
2. **Execute Conversion**: Once approved, run `DatasetConverter.convert_dataset(dry_run=False)` to write the clean YOLO structure to `data/processed/yolo/`.