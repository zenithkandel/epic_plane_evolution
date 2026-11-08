import os
import sys
import urllib.request

DEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "StreamingAssets", "aa", "WebGL")

MISSING_BUNDLES = [
    "00a4be9b31762d32fbd80a64c92a1f24.bundle",
    "00c7f2cea6935faebcffe7326fcbfefe.bundle",
    "0262b035448c8a4975a3f56c801dced6.bundle",
    "03160f4f96f0dd4e67256dcfb5cdbb78.bundle",
    "08e0950254833bc8226eea6dfebe8907.bundle",
    "11893afe7a18040b3eb9d44472ec28f2.bundle",
    "15523465cca91d161b38e5268f784eae.bundle",
    "18dd850238c658ebe176898d1be15ab2.bundle",
    "1a93bd5cec3872b016f174b0e9da1892.bundle",
    "1af6e17104a8de1228027aed92bcbd45.bundle",
    "1b24266b67b61883af6e5631839e3085.bundle",
    "1bdee23f5753a9447022ad75cf61a3ed.bundle",
    "1cd3810bcfba082a2893a1b326e6b6a3.bundle",
    "1e5c5165027e3766ee13d56b65b0bb00.bundle",
    "214a6aff16a7c080e21874c100c99422.bundle",
    "235eed293f9629f3f8b79b88d1e9fe0c.bundle",
    "239152fd9ce49cac2da2254d590e4c20.bundle",
    "24e41c439c820550842d51a926790712.bundle",
    "2a1db3b4812a0be12e7ed85827dc22ec.bundle",
    "2b95093fabc1819a1905e35ccc87c4f6.bundle",
    "2c8422649dd3701983af5ddd17e3da0e.bundle",
    "2caea261dd1e7e17695b75d3e8672579.bundle",
    "2dff656fb6facc926d7cad266468dc1f.bundle",
    "3232ecf1b4ed2e26622fd485c9740b2a.bundle",
    "352b276c55b8f55a4866a7ee83d4a400.bundle",
    "3966e5e5d6ca1c9938c22f54c859193b.bundle",
    "433d46861f87f229bca92bd162239f30.bundle",
    "434a3172ea254192fc35bc77bcea04d5.bundle",
    "4501a2fd148c4c7866a39193f6bce0fc.bundle",
    "45adabd63e7a4357847eb211fe2317bf.bundle",
    "4a93bb700489491116d0cdeaf82c414c.bundle",
    "4fdff4b3c8c9b42b2092a77675a70538.bundle",
    "5252cef0992379cf1e2296426fa37604.bundle",
    "5523c4189a289849137fc24fafeaaccb.bundle",
    "588ce50801e44c8de669b6bcffc54bc3.bundle",
    "60d3a0c26f7f8db3b0e610f265a51418.bundle",
    "64818549d7ec1a46b246c37468623de1.bundle",
    "74793eda3f7071bc3eb6a2842a94e06d.bundle",
    "75aa241b1d06bbdac5abf44c26ba9007.bundle",
    "7611ed41dc65c443d2de212cbcd52c8b.bundle",
    "82ebc6e0114da7a7be47faa9594761f0.bundle",
    "85090dd102331d3477a7160ca617d88d.bundle",
    "8caa5e21202e4436f5decc667c00d3da.bundle",
    "8d299d9a0788494e67c06cd67243e67d.bundle",
    "9007ee287ad35ee074baaedb5a459430.bundle",
    "9350ae735049b0d6fec1252f99ae30c2.bundle",
    "98b5317798a1e61bc384dd0d8888bfdb.bundle",
    "9feccb74f83eb77b78b01989ecf2c33f.bundle",
    "a1c915929d1aa5baaada7df29c106c33.bundle",
    "a3d0d9b7a5afa69d8e61792db0aac9db.bundle",
    "a7147182f26b8483d8f979cc42f56bcc.bundle",
    "b0326271d5ed1c2ac3aacaa623061c07.bundle",
    "b0f22ab83239f72317dcbf61af172ed3.bundle",
    "b138c25a2a587a1a31a324d94cfcdfe2.bundle",
    "b2cc63854761a67a9774058e4316d0a8.bundle",
    "b4299aedb4630120de7c070c69aeb4ef.bundle",
    "bc11a9dadf49b69e49c3e1626804c0ab.bundle",
    "bf262959d7fb218d4f86573afc4ba8c3.bundle",
    "biplanea_assets_all_2caea261dd1e7e17695b75d3e8672579.bundle",
    "biplaneb_assets_all_fc1ac1f12265b6adf19b6b2292eba94e.bundle",
    "biplanec_assets_all_235eed293f9629f3f8b79b88d1e9fe0c.bundle",
    "biplaned_assets_all_4501a2fd148c4c7866a39193f6bce0fc.bundle",
    "biplanee_assets_all_fc3991b4bc9df99aeb65a155c94203b3.bundle",
    "c01e27215c0a040ca2c4f4a2e45fa32f.bundle",
    "c0b53e1affa4bb88b7a06a2fb4ede925.bundle",
    "cardboardplanea_assets_all_3966e5e5d6ca1c9938c22f54c859193b.bundle",
    "cardboardplaneb_assets_all_1af6e17104a8de1228027aed92bcbd45.bundle",
    "cardboardplanec_assets_all_1cd3810bcfba082a2893a1b326e6b6a3.bundle",
    "cardboardplaned_assets_all_9feccb74f83eb77b78b01989ecf2c33f.bundle",
    "cardboardplanee_assets_all_434a3172ea254192fc35bc77bcea04d5.bundle",
    "ccac2c31d88bcfcc95dc938f69668658.bundle",
    "commercialplanea_assets_all_b0f22ab83239f72317dcbf61af172ed3.bundle",
    "commercialplaneb_assets_all_e43dc977365d201c6dd99107679d5df7.bundle",
    "commercialplanec_assets_all_e809189698815057638889ce58cc125e.bundle",
    "commercialplaned_assets_all_d82ba1af2ee91c829f1f3bfcb5588095.bundle",
    "commercialplanee_assets_all_45adabd63e7a4357847eb211fe2317bf.bundle",
    "d0d0ab912e0f313471898a44849cb5af.bundle",
    "d4b4e545b709006534535fac53150c24.bundle",
    "d60a78d8c30d64bdd588534d12b18b17.bundle",
    "d6bbfd7673adb48423d8842736102772.bundle",
    "d82ba1af2ee91c829f1f3bfcb5588095.bundle",
    "d9018a9ab9d5f9813dcad608fe9ce8d2.bundle",
    "e2f2f44cac50c6d130f4ad37b00d0027.bundle",
    "e43dc977365d201c6dd99107679d5df7.bundle",
    "e809189698815057638889ce58cc125e.bundle",
    "ee750b9c6ab3eabca01a5b630f911397.bundle",
    "f18308d4bb7b8bde0234ab6225cd1cde.bundle",
    "f25f0bed348c6ed44273d2b44b67b8c1.bundle",
    "f3e18df449aac826441ebaa84bde0cec.bundle",
    "f52067bcf19ebab9154aee8e4d623e92.bundle",
    "fc1ac1f12265b6adf19b6b2292eba94e.bundle",
    "fc3991b4bc9df99aeb65a155c94203b3.bundle",
    "fcd08b86213cc7494c00431d216353fb.bundle",
    "ff8e87dd6867b640f4e2650df323cf34.bundle",
    "gamestart_scenes_all_433d46861f87f229bca92bd162239f30.bundle",
    "packedassets0_scenes_all_214a6aff16a7c080e21874c100c99422.bundle",
    "packedassets1_scenes_all_5523c4189a289849137fc24fafeaaccb.bundle",
    "packedassets2_scenes_all_5252cef0992379cf1e2296426fa37604.bundle",
    "packedassets4_scenes_all_f52067bcf19ebab9154aee8e4d623e92.bundle",
    "packedassets5_scenes_all_1a93bd5cec3872b016f174b0e9da1892.bundle",
    "packedassets6_scenes_all_74793eda3f7071bc3eb6a2842a94e06d.bundle",
    "paperplanea_assets_all_4fdff4b3c8c9b42b2092a77675a70538.bundle",
    "paperplaneb_assets_all_b4299aedb4630120de7c070c69aeb4ef.bundle",
    "paperplanec_assets_all_7611ed41dc65c443d2de212cbcd52c8b.bundle",
    "paperplaned_assets_all_c0b53e1affa4bb88b7a06a2fb4ede925.bundle",
    "sharedassets_assets_assets_audio_sounds_splash_splash1.wav_ccac2c31d88bcfcc95dc938f69668658.bundle",
    "sharedassets_assets_assets_audio_sounds_splash_splash2.wav_f3e18df449aac826441ebaa84bde0cec.bundle",
    "sharedassets_assets_assets_scenes_levels_others_sabanalevel_reflectionprobe-0.exr_ee750b9c6ab3eabca01a5b630f911397.bundle",
    "sharedassets_assets_assets_standardassets_epictoonfx_textures_water_3x3.png_8caa5e21202e4436f5decc667c00d3da.bundle",
    "solarplanea_assets_all_9350ae735049b0d6fec1252f99ae30c2.bundle",
    "solarplaneb_assets_all_1e5c5165027e3766ee13d56b65b0bb00.bundle",
    "solarplanec_assets_all_b2cc63854761a67a9774058e4316d0a8.bundle",
    "solarplaned_assets_all_239152fd9ce49cac2da2254d590e4c20.bundle",
    "solarplanee_assets_all_03160f4f96f0dd4e67256dcfb5cdbb78.bundle",
    "toyplanea_assets_all_a1c915929d1aa5baaada7df29c106c33.bundle",
    "toyplaneb_assets_all_f25f0bed348c6ed44273d2b44b67b8c1.bundle",
    "toyplanec_assets_all_9007ee287ad35ee074baaedb5a459430.bundle",
    "toyplaned_assets_all_d9018a9ab9d5f9813dcad608fe9ce8d2.bundle",
    "toyplanee_assets_all_3232ecf1b4ed2e26622fd485c9740b2a.bundle",
    "vintageplanea_assets_all_a7147182f26b8483d8f979cc42f56bcc.bundle",
    "vintageplaneb_assets_all_b138c25a2a587a1a31a324d94cfcdfe2.bundle",
    "vintageplanec_assets_all_08e0950254833bc8226eea6dfebe8907.bundle",
    "vintageplaned_assets_all_00c7f2cea6935faebcffe7326fcbfefe.bundle",
    "vintageplanee_assets_all_588ce50801e44c8de669b6bcffc54bc3.bundle"
]

def main():
    if len(sys.argv) < 2:
        print("Usage: python download_missing_bundles.py <BASE_URL>")
        print("Example: python download_missing_bundles.py https://example.com/epic_plane")
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")
    if not base_url.endswith("StreamingAssets/aa/WebGL"):
        bundles_url = base_url + "/StreamingAssets/aa/WebGL"
    else:
        bundles_url = base_url

    os.makedirs(DEST_DIR, exist_ok=True)
    total = len(MISSING_BUNDLES)
    print(f"Downloading {total} missing bundles to {DEST_DIR}...")

    downloaded = 0
    failed = 0

    for idx, bundle in enumerate(MISSING_BUNDLES, 1):
        target_path = os.path.join(DEST_DIR, bundle)
        if os.path.exists(target_path):
            print(f"[{idx}/{total}] Already exists: {bundle}")
            continue

        file_url = f"{bundles_url}/{bundle}"
        print(f"[{idx}/{total}] Fetching {bundle}...")
        try:
            req = urllib.request.Request(file_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp:
                with open(target_path, "wb") as out_file:
                    out_file.write(resp.read())
            downloaded += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1

    print(f"\nDone! Downloaded: {downloaded}, Failed: {failed}")

if __name__ == "__main__":
    main()

