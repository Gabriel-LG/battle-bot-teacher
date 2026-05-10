serial.onDataReceived(serial.delimiters(Delimiters.CarriageReturn), function () {
    line = serial.readUntil(serial.delimiters(Delimiters.CarriageReturn))
    if (line == "mute") {
        for (let index = 0; index <= 15; index++) {
            teacher.enableSound(index, false)
            teacher.transmitState(index)
        }
        basic.showIcon(IconNames.No)
    } else if (line == "unmute") {
        for (let index = 0; index <= 15; index++) {
            teacher.enableSound(index, true)
            teacher.transmitState(index)
        }
        basic.showIcon(IconNames.Yes)
    }
})
let line = ""
serial.redirectToUSB()
let channel = 0
controller.initController(channel)
basic.showNumber(channel)
basic.pause(1000)
basic.clearScreen()
