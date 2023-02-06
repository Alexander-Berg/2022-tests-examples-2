#include <userver/utest/utest.hpp>

#include <models/laravel_token.hpp>
#include <userver/crypto/base64.hpp>

TEST(LaravelDecrypt, Base) {
  auto encrypted_base64 =
      "eyJpdiI6Ijd0OU9keDBvb1pPOE5DQVhoUjhIakE9PSIsInZhbHVlIjoibk5hcDA4T2FnQnNW"
      "VUpua1lVSEJRRjQrMFVVYXpnVyszY29lcVFpdWFNUmoxelV5bGUrOFFqMERHODcxMWFCRkhP"
      "TnByWnE5S210bUFCNnB5cXNZczErRW1VTm83Rmd3d0RvcDZBTHFjVE9pb0QwcmN5SVpySVZN"
      "S0VPRXlMVDJjV0dNS3hYMGVxQ3dGRE43cGVIdEFtZnBLaFwvQjBkeGp3K1NsVUtnaStOTT0i"
      "LCJtYWMiOiI0NzVlZjJhNjkwM2VjZTM4M2M3YTBlYjBiZWVhNWI1NWJjZTAxMzY4NTdjNTNm"
      "ZTMyNTBmODcyZTY3N2ZlZTE3In0=";
  auto key_base64 = "VsdbVZN1g+R6MmNXG4zwl9h0k8VYei3VjojIF6l7VqE=";
  fleet_authproxy::models::laravel::Decrypter d(key_base64);
  auto decrypted = d.Decrypt(encrypted_base64);
  auto expected = "AgAAAADuyyxgAAAQXG95Nfdbp03-sGEKpz8mVH4";
  EXPECT_EQ(decrypted, expected);
}
