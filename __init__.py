import Live

from _Framework.Capabilities import controller_id, inport, outport, CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, AUTO_LOAD_KEY

from .FatPig import FatPig

def create_instance(c_instance):
    c_instance.log_message("FatPig.__init__.#create_instance[initializing pork sluice]")
    return FatPig(c_instance)

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=4661, product_ids=[97], model_name='Launch Control XL'),
     PORTS_KEY: [inport(props=[NOTES_CC, SCRIPT]), outport(props=[NOTES_CC, SCRIPT])],
     AUTO_LOAD_KEY: True}
