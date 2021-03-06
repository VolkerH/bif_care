import os
import re
import pathlib
import javabridge as jv
import bioformats as bf
from collections import namedtuple

Axes = namedtuple("Axes", "t z c y x")
Reso = namedtuple("PixelSize", "X Y Z T Xunit Yunit Zunit Tunit")


def get_space_time_resolution(img_path):
    omexml = bf.get_omexml_metadata(img_path)

    om = bf.OMEXML(xml=omexml)
    i = om.image(0)

    # get frame intervall
    ##########################
    C = i.Pixels.get_SizeC()
    Z = i.Pixels.get_SizeZ()
    T = i.Pixels.get_SizeT()
    
    X_res = i.Pixels.get_PhysicalSizeX()
    Y_res = i.Pixels.get_PhysicalSizeY()
    Z_res = i.Pixels.get_PhysicalSizeZ()
    
    X_res_unit = i.Pixels.get_PhysicalSizeXUnit()
    Y_res_unit = i.Pixels.get_PhysicalSizeYUnit()
    Z_res_unit = i.Pixels.get_PhysicalSizeZUnit()
    
    if None in [X_res, Y_res]:
        X_res = Y_res = 1
    
    if None in [X_res_unit, Y_res_unit]:
        X_res_unit = Y_res_unit = "pixel"
        
    if Z_res is None:
        Z_res = 1
        Z_res_unit = "pixel"

    # check for \mu in string (argh)
    if '\xb5' in X_res_unit:
        X_res_unit = "micron"
        Y_res_unit = "micron"

    if '\xb5' in Z_res_unit:
        Z_res_unit = "micron"

    
    
        

    i.Pixels.get_PhysicalSizeZUnit()
    
    frame_interval = 0
    Tunit = "sec."
    
    if i.Pixels.node.get("TimeIncrement"):
        frame_interval = i.Pixels.node.get("TimeIncrement")
        Tunit = i.Pixels.node.get("TimeIncrementUnit")
        
    elif (T > 1) and i.Pixels.get_plane_count() > 0:
        plane_axes = i.Pixels.get_DimensionOrder().replace("X", "").replace("Y", "")

        stride_t = 1
        for axes in plane_axes.upper():
            if axes == "C":
                stride_t *= C
            if axes == "Z":
                stride_t *= Z

        t_end = stride_t * (T-1)

        print(i.Pixels.get_plane_count(),  t_end)
        t_end_plane = i.Pixels.Plane(t_end)

        frame_interval = t_end_plane.DeltaT / T

    return Reso(X_res, Y_res, Z_res, frame_interval, X_res_unit, Y_res_unit, Z_res_unit, Tunit)



class JVM(object):
    log_config = os.path.join(os.path.dirname(__file__), "res/log4j.properties")
    started = False

    def start(self):
        if not JVM.started:
            jv.start_vm(class_path=bf.JARS, 
                        max_heap_size='8G', 
                        args=["-Dlog4j.configuration=file:{}".format(self.log_config),],
                        run_headless=True)
            JVM.started = True

    def shutdown(self):
        if JVM.started:
            jv.kill_vm()
            JVM.started = False

def get_pixel_dimensions(fn):
    JVM().start()
 
    ir = bf.ImageReader(str(fn))
    
    t_size = ir.rdr.getSizeT()
    z_size = ir.rdr.getSizeZ()
    c_size = ir.rdr.getSizeC()
    y_size = ir.rdr.getSizeY()
    x_size = ir.rdr.getSizeX()
    
    ir.close()
    return Axes(t_size, z_size, c_size, y_size, x_size)

def get_file_list(in_dir, glob):
    assert os.path.exists(in_dir), "Folder '{}' does not exist".format(in_dir)
    return sorted(list( pathlib.Path(in_dir).glob(glob)))

def check_file_lists(in_dir, low_wc, high_wc):
    from fnmatch import translate
    fl_low  = get_file_list(in_dir, low_wc)
    fl_high = get_file_list(in_dir, high_wc)

    if len(fl_low) == 0:
        return False, "No files selected"

    if len(fl_low) != len(fl_high):
        return False, "Number of files does not match {} != {}".format(len(fl_low), len(fl_high))

    for fl, fh in zip(fl_low, fl_high):
        if os.path.splitext(fl.name)[1] != os.path.splitext(fh.name)[1]:
            return False, "Extensions do not match"

        dim_low  = get_pixel_dimensions(fl)
        dim_high = get_pixel_dimensions(fh)

        if dim_low.c != dim_high.c:
            return False, "Low and high quality images have different channels\n '{}' != '{}'".format(fl, fh)

        if dim_low.t != dim_high.t:
            return False, "Low and high quality images have different number of time points\n '{}' != '{}'".format(fl, fh)
        
        if (dim_low.x > dim_high.x) or \
           (dim_low.y > dim_high.y) or \
           (dim_low.z > dim_high.z):
           return False, "Low quality images have higher spatial resolution"

        if (dim_low.t > dim_low.z) and \
            (dim_low.z == 1):
            return False, "Only 1 z-slice in '{}' but {} frames. Make sure input images are Z-stacks.".format(fl, dim_low.t)

    return True, "OK"




    





def get_upscale_factors(in_dir, low_wc, high_wc): 
    low_fl = get_file_list(in_dir, low_wc)
    high_fl = get_file_list(in_dir, high_wc)        

    low_dim  = get_pixel_dimensions(str(low_fl[0]))
    high_dim = get_pixel_dimensions(str(high_fl[0]))

    return (high_dim.z / low_dim.z,
            high_dim.y / low_dim.y,
            high_dim.x / low_dim.x)

