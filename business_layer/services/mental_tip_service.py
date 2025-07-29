from data_layer.api.mental_tip_api import MentalTipAPI

class MentalTipService:
    mood_map = {
        1: "Very Bad",
        2: "Not great",
        3: "Okay",
        4: "Good",
        5: "Great"
    }

    @staticmethod
    async def get_mental_tip(mood_level: int) -> str:
        keyword = MentalTipService.mood_map.get(mood_level, "wellbeing")
        return await MentalTipAPI.fetch_tip_from_api(keyword)