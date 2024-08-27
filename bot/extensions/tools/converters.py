from enum import StrEnum
from logging import getLogger

from discord import ApplicationContext as AppCtx
from discord import SlashCommandGroup, option

from bot.classes.edgar_bot import EdgarBot
from bot.classes.extension import Extension

log = getLogger(__name__)


class TemperatureUnits(StrEnum):
    FAHRENHEIT = "fahrenheit"
    CELSIUS = "celsius"
    KELVIN = "kelvin"


TEMPERATURE_UNITS = [temperature_unit.name.capitalize() for temperature_unit in TemperatureUnits]


class Converters(Extension):
    converters = SlashCommandGroup("convert", "Converts something to something.")

    @converters.command(name="temperature", description="Converts temperature.")
    @option("amount", description="Temperature value for conversion.")
    @option("from_type", description="Initial unit of temperature.", choices=TEMPERATURE_UNITS)
    @option("to_type", description="Converted unit of temperature.", choices=TEMPERATURE_UNITS)
    @option("number_of_decimal_places", description="Number of digits after the decimal point.", choices=[1, 2, 3])
    async def convert_temperature(
        self,
        ctx: AppCtx,
        amount: float,
        from_type: str,
        to_type: str,
        number_of_decimal_places: int = 1
    ) -> None:
        absolute_zero_in_celsius = 273.15

        from_type = from_type.lower()
        to_type = to_type.lower()

        if from_type == to_type:
            await ctx.respond(f"Variables have one type - {from_type} and {to_type}. The answer is: `{amount}`")
            return

        result = 0
        match from_type:
            case TemperatureUnits.CELSIUS:
                match to_type:
                    case TemperatureUnits.FAHRENHEIT:
                        result = round((amount * 1.8) + 32, number_of_decimal_places)
                    case TemperatureUnits.KELVIN:
                        result = round(amount + absolute_zero_in_celsius, number_of_decimal_places)

            case TemperatureUnits.FAHRENHEIT:
                match to_type:
                    case TemperatureUnits.CELSIUS:
                        result = round((amount - 32) / 1.8, number_of_decimal_places)
                    case TemperatureUnits.KELVIN:
                        result = round((amount - 32) * 5 / 9 + absolute_zero_in_celsius, number_of_decimal_places)

            case TemperatureUnits.KELVIN:
                match to_type:
                    case TemperatureUnits.CELSIUS:
                        result = round(amount - absolute_zero_in_celsius, number_of_decimal_places)
                    case TemperatureUnits.FAHRENHEIT:
                        result = round((amount - absolute_zero_in_celsius) * 1.8 + 32, number_of_decimal_places)

        log.debug("Converter: '%s' converts %s '%s' to %s '%s'", ctx.author.name, amount, from_type, result, to_type)
        await ctx.respond(f"`{amount}` {from_type} should be equal to `{result}` {to_type}")


def setup(bot: EdgarBot):
    bot.add_cog(Converters(bot))
