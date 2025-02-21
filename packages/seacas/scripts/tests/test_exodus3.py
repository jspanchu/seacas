#!/usr/bin/env python
"""
Copyright(C) 1999-2022 National Technology & Engineering Solutions
of Sandia, LLC (NTESS).  Under the terms of Contract DE-NA0003525 with
NTESS, the U.S. Government retains certain rights in this software.

See packages/seacas/LICENSE for details

"""

import unittest
import sys
import os
import tempfile
import ctypes
from contextlib import contextmanager

ACCESS = os.getenv('ACCESS', '@ACCESSDIR@')
sys.path.append(os.path.join(ACCESS, "lib"))
import exodus as exo



class TestAssemblies(unittest.TestCase):

    def setUp(self):
        input_dir = os.path.dirname(__file__)
        self.tempdir = tempfile.TemporaryDirectory()
        self.temp_exo_path = os.path.join(self.tempdir.name, "temp-test-assembly.exo")
        with exo.exodus(os.path.join(input_dir, "test-assembly.exo"), mode='r') as exofile:
            self.exofile = exofile
            with self.exofile.copy(self.temp_exo_path, True) as temp_exofile:
                self.temp_exofile = temp_exofile

    def tearDown(self):
        self.tempdir.cleanup()

    def test_ex_obj_to_inq(self):
        self.assertEqual("EX_INQ_ASSEMBLY", exo.ex_obj_to_inq('EX_ASSEMBLY'))

    def test_ex_obj_to_inq_wrong_obj_type(self):
        self.assertEqual(-1, exo.ex_obj_to_inq('fake_obj'))

    def test_ex_entity_type_to_objType(self):
        self.assertEqual("assembly", exo.ex_entity_type_to_objType(exo.get_entity_type('EX_ASSEMBLY')))

    def test_ex_entity_type_to_objType_wrong_entity_type(self):
        self.assertEqual("EX_INVALID", exo.ex_entity_type_to_objType('fake_entity'))

    def test_exodus_context_manager_reraises_exceptions(self):
        with self.assertRaises(AssertionError):
            with exo.exodus(self.temp_exo_path, mode='r'):
                self.assertFalse(True)

    def test_copy_opened_in_append_mode(self):
        new = exo.assembly(name='Unit_test', type=exo.ex_entity_type.EX_ASSEMBLY, id=444)
        new.entity_list = [100, 222]
        temp_exo_path2 = self.temp_exo_path+'2'
        with exo.exodus(self.temp_exo_path, mode='r') as temp_exofile:
            expected = [assem for assem in temp_exofile.get_ids('EX_ASSEMBLY')]
            with temp_exofile.copy(temp_exo_path2, True, mode='a') as temp_exofile2:
                temp_exofile2.put_assembly(new)
                copied_output = [assem for assem in temp_exofile2.get_ids('EX_ASSEMBLY')]
                self.assertNotEqual(temp_exofile.modeChar, temp_exofile2.modeChar)
        self.assertNotEquals(expected, copied_output)

    def test_copy_opened_in_read_mode(self):
        temp_exo_path2 = self.temp_exo_path+'2'
        with exo.exodus(self.temp_exo_path, mode='r') as temp_exofile:
            with temp_exofile.copy(temp_exo_path2, True, mode='r') as temp_exofile2:
                expected = [assem for assem in temp_exofile.get_ids('EX_ASSEMBLY')]
                copied_output = [assem for assem in temp_exofile2.get_ids('EX_ASSEMBLY')]
                self.assertEqual(temp_exofile.modeChar, temp_exofile2.modeChar)
        self.assertEquals(expected, copied_output)

    def test_setup_ex_assembly(self):
        assem = exo.assembly(name='Unit_test', type='EX_ASSEMBLY', id=444)
        assem.entity_list = [100, 222]
        ctype_assem = exo.setup_ex_assembly(assem)
        self.assertIsInstance(ctype_assem, exo.ex_assembly)
        self.assertIsInstance(ctype_assem.entity_list, ctypes.POINTER(ctypes.c_longlong))

    def test_get_name_assembly(self):
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            assembly_ids = temp_exofile.get_ids("EX_ASSEMBLY")
            names = [temp_exofile.get_name("EX_ASSEMBLY", assembly) for assembly in assembly_ids]
        self.assertEqual(['Root', 'Child2', 'Child3', 'Child4', 'NewAssembly', 'FromPython'], names)

    def test_inquire_assembly(self):
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            assem_count = temp_exofile.inquire("EX_INQ_ASSEMBLY")
        self.assertEqual(6, assem_count)

    def test_get_block_id_map(self):
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            elem_ids = temp_exofile.get_ids("EX_ELEM_BLOCK")
            expected = [1, 2, 3, 4, 5, 6, 7]
            outputs = []
            for val in elem_ids:
                outputs.extend(temp_exofile.get_block_id_map("EX_ELEM_BLOCK", val))
        self.assertListEqual(expected, outputs)

    def test_get_assembly(self):
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            assembly_ids = temp_exofile.get_ids("EX_ASSEMBLY")
            assemblies = [temp_exofile.get_assembly(assembly) for assembly in assembly_ids]
        root = exo.assembly(name='Root', type='EX_ASSEMBLY', id=100)
        root.entity_list = [100, 200, 300, 400]
        self.assertEqual(str(root), str(assemblies[0]))

    def test_get_assemblies(self):
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            assembly_ids = temp_exofile.get_ids("EX_ASSEMBLY")
            assemblies = temp_exofile.get_assemblies(assembly_ids)
        expected = [exo.assembly(name='Root', type='EX_ASSEMBLY', id=100),
                    exo.assembly(name='Child2', type='EX_ELEM_BLOCK', id=200),
                    exo.assembly(name='Child3', type='EX_ELEM_BLOCK', id=300),
                    exo.assembly(name='Child4', type='EX_ELEM_BLOCK', id=400),
                    exo.assembly(name='NewAssembly', type='EX_ASSEMBLY', id=222),
                    exo.assembly(name='FromPython', type='EX_ASSEMBLY', id=333)]
        for i, x in enumerate(expected):
            entity_lists = [[100, 200, 300, 400],
                            [10, 11, 12, 13],
                            [14, 15, 16],
                            [10, 16],
                            [100, 200, 300, 400],
                            [100, 222]]
            x.entity_list = entity_lists[i]
        self.maxDiff = None
        self.assertEqual(str(expected), str(assemblies))

    def test_put_qa(self):
        new = [("name","1.2.3-4","20220801","12:34:56")]
        with exo.exodus(self.temp_exo_path, mode='a') as temp_exofile:
            temp_exofile.put_qa_records(new)
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            self.assertEqual(new, temp_exofile.get_qa_records())

    def test_put_assembly(self):
        new = exo.assembly(name='Unit_test', type=exo.ex_entity_type.EX_ASSEMBLY, id=444)
        new.entity_list = [100, 222]
        with exo.exodus(self.temp_exo_path, mode='a') as temp_exofile:
            temp_exofile.put_assembly(new)
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            assembly_ids = temp_exofile.get_ids("EX_ASSEMBLY")
            assemblies = [temp_exofile.get_assembly(assembly) for assembly in assembly_ids]
        self.assertEqual(new.name, assemblies[6].name)
        self.assertEqual(16, assemblies[6].type)
        self.assertEqual(new.id, assemblies[6].id)
        self.assertEqual(new.entity_list, assemblies[6].entity_list)

    def test_get_reduction_variables_assembly(self):
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            red_var = temp_exofile.get_reduction_variable_number("EX_ASSEMBLY")
            names = temp_exofile.get_reduction_variable_names("EX_ASSEMBLY")
        self.assertEqual(4, red_var)
        self.assertIn("Momentum_X", names)
        self.assertIn("Momentum_Y", names)
        self.assertIn("Momentum_Z", names)
        self.assertIn("Kinetic_Energy", names)

    def test_get_reduction_variables_assembly_enum(self):
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            red_var = temp_exofile.get_reduction_variable_number(exo.ex_entity_type.EX_ASSEMBLY)
            names = temp_exofile.get_reduction_variable_names(exo.ex_entity_type.EX_ASSEMBLY)
        self.assertEqual(4, red_var)
        self.assertIn("Momentum_X", names)
        self.assertIn("Momentum_Y", names)
        self.assertIn("Momentum_Z", names)
        self.assertIn("Kinetic_Energy", names)

    def test_get_reduction_variable_assembly(self):
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            red_var = temp_exofile.get_reduction_variable_number("EX_ASSEMBLY")
            name = temp_exofile.get_reduction_variable_name("EX_ASSEMBLY", 1)
        self.assertEqual(4, red_var)
        self.assertIn("Momentum_X", name)

    def test_get_reduction_variable_assembly_enum(self):
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            red_var = temp_exofile.get_reduction_variable_number(exo.ex_entity_type.EX_ASSEMBLY)
            name = temp_exofile.get_reduction_variable_name(exo.ex_entity_type.EX_ASSEMBLY, 1)
        self.assertEqual(4, red_var)
        self.assertIn("Momentum_X", name)

    def test_get_reduction_variable_values_assembly(self):
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            assembly_ids = temp_exofile.get_ids("EX_ASSEMBLY")
            assemblies = [temp_exofile.get_assembly(assembly) for assembly in assembly_ids]
            values = temp_exofile.get_reduction_variable_values('EX_ASSEMBLY', assemblies[0].id, 1)
        self.assertListEqual([0.02, 0.03, 0.04, 0.05], list(values))

    def test_get_reduction_variable_values_assembly_no_values(self):
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            assembly_ids = temp_exofile.get_ids("EX_ASSEMBLY")
            assemblies = [temp_exofile.get_assembly(assembly) for assembly in assembly_ids]
            values = temp_exofile.get_reduction_variable_values('EX_ASSEMBLY', assemblies[5].id, 1)
        self.assertListEqual([0.00, 0.00, 0.00, 0.00], list(values))

    def test_put_assemblies(self):
        new = exo.assembly(name='Unit_test', type='EX_ASSEMBLY', id=444)
        new.entity_list = [100, 222]
        with exo.exodus(self.temp_exo_path, mode='a') as temp_exofile:
            temp_exofile.put_assemblies([new])
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            assembly_ids = temp_exofile.get_ids("EX_ASSEMBLY")
            assemblies = [temp_exofile.get_assembly(assembly) for assembly in assembly_ids]
        self.assertEqual(new.name, assemblies[6].name)
        self.assertEqual(16, assemblies[6].type)
        self.assertEqual(new.id, assemblies[6].id)
        self.assertEqual(new.entity_list, assemblies[6].entity_list)

    def test_put_assemblies_multiple_assemblies(self):
        new = exo.assembly(name='Unit_test1', type='EX_ASSEMBLY', id=444)
        new.entity_list = [100, 222]
        new2 = exo.assembly(name='Unit_test2', type='EX_ASSEMBLY', id=448)
        new2.entity_list = [102, 224]
        with exo.exodus(self.temp_exo_path, mode='a') as temp_exofile:
            temp_exofile.put_assemblies([new, new2])
        with exo.exodus(self.temp_exo_path) as temp_exofile:
            assembly_ids = temp_exofile.get_ids("EX_ASSEMBLY")
            assemblies = [temp_exofile.get_assembly(assembly) for assembly in assembly_ids]
        self.assertEqual(new.name, assemblies[6].name)
        self.assertEqual(16, assemblies[6].type)
        self.assertEqual(new.id, assemblies[6].id)
        self.assertEqual(new.entity_list, assemblies[6].entity_list)

        self.assertEqual(new2.name, assemblies[7].name)
        self.assertEqual(16, assemblies[7].type)
        self.assertEqual(new2.id, assemblies[7].id)
        self.assertEqual(new2.entity_list, assemblies[7].entity_list)


class TestExodusUtilities(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_basename(self):
        self.assertEqual("test", exo.basename("test.e"))
        self.assertEqual("fake/path/to/test", exo.basename("fake/path/to/test.e"))

    def test_getExodusVersion(self):
        include_path = os.path.join(self.tempdir.name, "include")
        os.makedirs(include_path)
        with open(os.path.join(include_path, "exodusII.h"), 'w') as fptr:
            fptr.write("#define EXODUS_VERSION_MAJOR 1\n")
            fptr.write("#define EXODUS_VERSION_MINOR 22\n")
        with swap_ACCESS_value(self.tempdir.name):
            self.assertEqual(122, exo.getExodusVersion())

    def test_getExodusVersion_not_found(self):
        include_path = os.path.join(self.tempdir.name, "include")
        os.makedirs(include_path)
        with open(os.path.join(include_path, "exodusII.h"), 'w') as fptr:
            fptr.write("#define NOT_EXODUS_VERSION 1\n")
            fptr.write("#define ALSO_NOT_EXODUS_VERSION 22\n")
        with swap_ACCESS_value(self.tempdir.name):
            self.assertEqual(0, exo.getExodusVersion())


@contextmanager
def swap_ACCESS_value(new_access_value):
    old_value = exo.ACCESS
    exo.ACCESS = new_access_value
    yield
    exo.ACCESS = old_value


if __name__ == '__main__':
    unittest.main()
