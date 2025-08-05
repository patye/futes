import logging

class HmvDecision:

  def hmv_decision(self, hmv_on, temperature):
      logger = logging.getLogger()
      logger.setLevel(logging.INFO)

      # define file handler and set formatter
      formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
      file_handler = logging.FileHandler('/var/log/heating/heating.log')
      file_handler.setFormatter(formatter)

      # add file handler to logger
      logger.addHandler(file_handler)


      logger.info("Temperature is: " + str(temperature))

      global boiler
      hmv_hysteresis = {
        "temp_low": 35,
        "temp_high": 55
      }
      if hmv_on and temperature >= hmv_hysteresis["temp_high"]:
          boiler = False
          logger.info("Boiler is: %s", boiler)
      elif hmv_on and temperature <= hmv_hysteresis["temp_low"]:
          boiler = True
          logger.info("Boiler is: %s", boiler)
      return boiler




