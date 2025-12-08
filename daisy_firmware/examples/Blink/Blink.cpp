#include "daisy_seed.h"

// Use the daisy namespace to prevent having to type
// daisy:: before all libdaisy functions
using namespace daisy;

// Declare a DaisySeed object called hardware
DaisySeed hardware;

void Callback(void* data)
{
    /** Use system time to blink LED once per second (1023ms) */
    bool led_state = (System::GetNow() & 1023) > 511;
    /** Set LED */
    hardware.SetLed(led_state);
}

int main(void)
{
    // Declare a variable to store the state we want to set for the LED.
    bool led_state;
    led_state = true;

    TimerHandle tim5;
    TimerHandle::Config tim_cfg;

    // Configure and Initialize the Daisy Seed
    // These are separate to allow reconfiguration of any of the internal
    // components before initialization.
    hardware.Configure();
    hardware.Init();

    /** TIM5 with IRQ enabled */
    tim_cfg.periph = TimerHandle::Config::Peripheral::TIM_5;
    tim_cfg.enable_irq = true;

    /** Configure frequency (30Hz) */
    auto tim_target_freq = 30;
    auto tim_base_freq   = System::GetPClk2Freq();
    tim_cfg.period       = tim_base_freq / tim_target_freq; 

    /** Initialize timer */
    tim5.Init(tim_cfg);
    tim5.SetCallback(Callback);

    /** Start the timer, and generate callbacks at the end of each period */
    tim5.Start();

    // Loop forever
    // for (;;)
    // {
    //     // Set the onboard LED
    //     hardware.SetLed(led_state);

    //     // Toggle the LED state for the next time around.
    //     led_state = !led_state;

    //     // Wait 500ms
    //     System::Delay(250);
    // }
}
