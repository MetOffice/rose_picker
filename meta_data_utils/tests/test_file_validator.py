from file_validator import validate_names

good_file_name = 'trunk/miniapps/diagnostics/source/diagnostics_meta/' \
                 'test_section__test_group__meta_mod.f90'
bad_file_names = ['trunk/miniapps/diagnostics/source/diagnostics_meta/'
                  'test_section__test_group__',
                  'trunk/miniapps/diagnostics/source/diagnostics_meta/'
                  'test_section__test_groupmeta_mod.f90',
                  'trunk/miniapps/diagnostics/source/diagnostics_meta/'
                  'test_section__test_group__.f90',
                  'trunk/miniapps/diagnostics/source/diagnostics_meta/'
                  'test_section__test_group.f90',
                  'trunk/miniapps/diagnostics/source/diagnostics_meta/'
                  'test_section__test_group__meta_mod']

matching_file_name = 'trunk/miniapps/diagnostics/source/diagnostics_meta/' \
                 'test_section__test_group__meta_mod.f90'
non_matching_file_name = 'trunk/miniapps/diagnostics/source/diagnostics_meta/' \
                 'not_test_section__test_group__meta_mod.f90'

good_module_name = "test_section__test_group__meta_mod"

bad_module_names = ["test_sectiontest_group__meta_mod",
                    "test_section__test_groupmeta_mod",
                    "test_section__test_group__metamod",
                    "test_section__test_group"]

matching_module_name = "test_section__test_group__meta_mod"
non_matching_module_name = "not_test_section__test_group__meta_mod"

good_meta_type_name = "test_section__test_group__meta_type"

bad_meta_type_names = ["test_section__test_group__",
                       "test_section__test_groupmeta_type",
                       "test_sectiontest_group__meta_type",
                       "__test_group__meta_type",
                       "test_section__test_group__meta_pe",
                       "test_section__test_group__metatype",
                       "__meta_type"]

matching_meta_type_name = "test_section__test_group__meta_type"
non_matching_meta_type_name = "not_test_section__test_group__meta_type"

good_group_name = "test_section__test_group"

bad_group_names = ["test_sectiontest_group",
                   "test_section_test_group",
                   ""]

matching_group_name = "test_section__test_group"
non_matching_group_name = "test_section__not_test_group"


def test_validate_names(caplog):

    result = validate_names(good_file_name,
                            good_module_name,
                            good_meta_type_name,
                            good_group_name)

    assert result is True


def test_validate_names_bad_file_name(caplog):

    for bad_file_name in bad_file_names:
        result = validate_names(bad_file_name,
                                good_module_name,
                                good_meta_type_name,
                                good_group_name)

        assert result is False
        assert "Filename in path is not correct" in caplog.text
        assert bad_file_name in caplog.text


def test_validate_names_bad_module_name(caplog):

    for bad_module_name in bad_module_names:
        result = validate_names(good_file_name,
                                bad_module_name,
                                good_meta_type_name,
                                good_group_name)

        assert result is False
        assert "Module in file is not correct" in caplog.text
        assert bad_module_name in caplog.text


def test_validate_names_meta_type(caplog):

    for bad_meta_type_name in bad_meta_type_names:
        result = validate_names(good_file_name,
                                good_module_name,
                                bad_meta_type_name,
                                good_group_name)

        assert result is False
        assert "meta_type_name in file is not correct" in caplog.text
        assert bad_meta_type_name in caplog.text


def test_validate_names_group_name(caplog):

    for bad_group_name in bad_group_names:
        result = validate_names(good_file_name,
                                good_module_name,
                                good_meta_type_name,
                                bad_group_name)

        assert result is False
        assert "group_name in file is not correct" in caplog.text
        assert bad_group_name in caplog.text


def test_validate_name_matching(caplog):

    result = validate_names(matching_file_name,
                            matching_module_name,
                            matching_meta_type_name,
                            matching_group_name)
    assert result is True


def test_validate_name_non_matching_file_name(caplog):

    result = validate_names(non_matching_file_name,
                            matching_module_name,
                            matching_meta_type_name,
                            matching_group_name)
    assert result is False
    assert "Section names do not match" in caplog.text


def test_validate_name_non_matching_module_name(caplog):
    result = validate_names(matching_file_name,
                            non_matching_module_name,
                            matching_meta_type_name,
                            matching_group_name)
    assert result is False
    assert "Section names do not match in" in caplog.text


def test_validate_name_non_matching_meta_type_name(caplog):
    result = validate_names(matching_file_name,
                            matching_module_name,
                            non_matching_meta_type_name,
                            matching_group_name)
    assert result is False
    assert "Bad meta_type name in" in caplog.text


def test_validate_name_non_matching_group_name(caplog):

    result = validate_names(matching_file_name,
                            matching_module_name,
                            matching_meta_type_name,
                            non_matching_group_name)
    assert result is False
    assert "Group names do not match in" in caplog.text
