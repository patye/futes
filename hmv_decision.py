class HmvDecision:


  def hmv_decision(self, hmv_on, temperature):

      global boiler
      hmv_hysteresis = {
        "temp_low": 35,
        "temp_high": 55
      }
      if hmv_on and temperature >= hmv_hysteresis["temp_high"]:
          boiler = False
      elif hmv_on and temperature <= hmv_hysteresis["temp_low"]:
          boiler = True
      return boiler




