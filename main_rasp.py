import hardware
import walkE_cache
import walkE_admin

DIST = 0.22/20 # Circumference of Wheel = 0.22m

encoder_list = hardware.encoder_init()

# try:
while True:    
    encoder_result = hardware.encoder_stateChange(encoder_list[-1], 1)
    
    print("Encoder 1:", encoder_result["count_one"], ", Encoder 2:", encoder_result["count_two"])

    encoder_list.append(encoder_result)    
    
    # hardware.motor_drive(*[100,90])
        
# except KeyboardInterrupt:

#     hardware.motor_drive(*[0,0])
    
#     # Cache Optical Encoder Data
#     walkE_cache.cache_encode("testjoint_data", encoder_list)

print("Complete")

hardware.motor_drive(*[0,0])