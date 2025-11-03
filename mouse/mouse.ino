#include <hidboot.h>
#include <usbhub.h>
#include <Mouse.h>
#include <hiduniversal.h>
#include <Wire.h>
#include <SPI.h>

#define RPT_LEN      8
#define BUFFER_SIZE 10  // Buffer for serial input parsing

USB       Usb;
USBHub    Hub(&Usb);
HIDUniversal Hid(&Usb);

class HIDMouseEvents {
  public:
    // Whenever a real-mouse button is pressed, forward it immediately:
    void OnButtonDn(uint8_t but_id) {
      Mouse.press(but_id);
    }
    void OnButtonUp(uint8_t but_id) {
      Mouse.release(but_id);
    }
    // Whenever the real-mouse moves/scrolls, forward that, too:
    void Move(int8_t xm, int8_t ym, int8_t scr) {
      Mouse.move(xm, ym, scr);
    }
};

class HIDMouseReportParser : public HIDReportParser {
    HIDMouseEvents *mouEvents;
    uint8_t oldButtons;
  public:
    HIDMouseReportParser(HIDMouseEvents *evt) : mouEvents(evt), oldButtons(0) {}

    void Parse(USBHID *hid, bool is_rpt_id, uint8_t len, uint8_t *buf) {
      uint8_t buttons = buf[0];  // bitfield of Button0 (LSB) .. Button4 (bit4)
      
      // Check each button bit: 1=Left, 2=Right, 4=Middle, 8=XB1, 16=XB2
      // (we extend the loop from <=4 up to <=16)
      for (uint8_t but_id = 1; but_id <= 16; but_id <<= 1) {
        bool wasPressed = oldButtons & but_id;
        bool isPressed  = buttons    & but_id;

        if (wasPressed != isPressed) {
          if (isPressed)    mouEvents->OnButtonDn(but_id);
          else              mouEvents->OnButtonUp(but_id);
        }
      }
      oldButtons = buttons;

      // Now forward any movement/scroll
      int8_t xm  = buf[2];
      int8_t ym  = buf[4];
      int8_t scr = buf[6];
      if (xm || ym || scr) {
        mouEvents->Move(xm, ym, scr);
      }
    }
};

HIDMouseEvents      MouEvents;
HIDMouseReportParser Mou(&MouEvents);
HIDBoot<USB_HID_PROTOCOL_MOUSE> HidMouse(&Usb);

char    received_code[BUFFER_SIZE];
uint8_t index1 = 0;

void setup() {
  Mouse.begin();
  Serial.begin(9600);
  Serial.setTimeout(1);
  Usb.Init();
  Hid.SetReportParser(0, &Mou);  // install our parser
}

void loop() {
  Usb.Task();  // handle real-mouse USB events first

  // If Python has sent us "x,y*" over Serial, parse it now:
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '*') {
      received_code[index1] = '\0';
      char *comma_pos = strchr(received_code, ',');
      if (comma_pos) {
        *comma_pos = '\0';
        int x_v = atoi(received_code);
        int y_v = atoi(comma_pos + 1);

        // Exactly as before: move‐and‐right-click
        Mouse.move(x_v, y_v, 0);
        Mouse.click(MOUSE_RIGHT);
      }
      index1 = 0;
    }
    else if (index1 < BUFFER_SIZE - 1) {
      received_code[index1++] = c;
    }
  }
}
