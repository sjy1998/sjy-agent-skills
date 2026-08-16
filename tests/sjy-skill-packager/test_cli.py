def test_public_contract_is_defined(packager):
    assert packager.PackageStatus.SUCCESS.value == "SUCCESS"
    assert packager.PackageStatus.FAIL.value == "FAIL"
    assert packager.PackageStatus.NEEDS_ADAPTATION.value == "NEEDS_ADAPTATION"
    assert packager.PackageStatus.AMBIGUOUS.value == "AMBIGUOUS"
    assert packager.EXIT_SUCCESS == 0
    assert packager.EXIT_FAIL == 1
    assert packager.EXIT_NEEDS_ADAPTATION == 2
    assert packager.EXIT_AMBIGUOUS == 3
    assert callable(packager.resolve_skill)
    assert callable(packager.validate_skill)
    assert callable(packager.build_zip)
    assert callable(packager.verify_zip)
    assert callable(packager.package_skill)
