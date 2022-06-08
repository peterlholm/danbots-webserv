"decode and set params from url"
from hw.led_control import set_flash, set_dias

# camera

def get_fix_param(request, camera):
    "decode and set camera param from parameters"
    exp = float(request.args.get('exp',0))
    iso = float(request.args.get('iso',0))
    if exp != 0:
        camera.shutter_speed = int (exp*1000000)
    if iso != 0:
        camera.iso = int(iso)

# led

def get_set_led(request):
    "Decode led information from url"
    # 1.003 sec on slow connections
    #start  = perf_counter()
    dias = float(request.args.get('dias',0))
    set_dias(dias)
    flash = float(request.args.get('flash',0))
    set_flash(flash)
    #stop = perf_counter()
    #print (f"GetSetLed {stop - start:.3f} seconds")
    return "dias="+str(dias) +"&flash="+str(flash)
