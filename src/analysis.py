from datetime import datetime, timedelta
import logging
import os

class UsageAnalyzer:
    """负责分析用电数据并进行预测。"""



    @staticmethod
    def predict_runout_date(usage_history: list, current_balance: float):
        """
        分析历史数据，计算每日平均用电量，并预测余额耗尽日期。
        :param current_balance: 当前的电费余额。
        :return: 一个包含分析结果的字符串，或在无法分析时返回None。
        """
        logging.info("开始预测电量耗尽日期...")
        try:
            # 1. 数据清洗和准备
            dates = []
            daily_usage = []
            skipped_count = 0
            
            # 只使用最近7天的数据进行预测
            for record in usage_history[:7]:
                # 仅使用有明确日用电量的记录进行分析
                if 'time' in record and 'dailyUsedEleQuantity' in record:
                    try:
                        usage_value = float(record['dailyUsedEleQuantity'])
                        # 过滤掉用电量为0的异常天数（可能是假期或数据缺失）
                        if usage_value > 0:
                            dates.append(datetime.strptime(record['time'], '%Y-%m-%d'))
                            daily_usage.append(usage_value)
                        else:
                            skipped_count += 1
                    except (ValueError, TypeError) as e:
                        logging.warning(f"跳过格式错误或数据无效的记录: {record}, 错误: {e}")
                        skipped_count += 1
                        continue
            
            if skipped_count > 0:
                logging.info(f"已过滤掉 {skipped_count} 条无效或用电量为0的记录。")
            
            if len(dates) < 2:
                logging.warning("近7天有效历史数据点不足（少于2个），无法进行预测。")
                return None

            # 2. 计算平均每日消耗量
            avg_daily_consumption = sum(daily_usage) / len(daily_usage)

            if avg_daily_consumption <= 0:
                logging.info("日均消耗量为0或负数，无法预测。")
                return None

            # 3. 预测耗尽日期
            days_left = current_balance / avg_daily_consumption
            predicted_date = datetime.now() + timedelta(days=days_left)

            logging.info(f"预测完成：日均消耗 ≈ {avg_daily_consumption:.2f}度, 预计剩余天数 ≈ {days_left:.1f}天")

            return {
                'avg_daily_consumption': round(avg_daily_consumption, 2),
                'days_left': round(days_left, 1),
                'predicted_date': predicted_date.strftime('%Y-%m-%d')
            }

        except Exception as e:
            logging.error(f"预测电量耗尽日期时发生错误: {e}")
            return None

    @staticmethod
    def check_low_balance_alert(current_balance: float):
        """
        检查当前电量是否低于告警阈值。
        :param current_balance: 当前剩余电量。
        :return: 如果低于阈值，返回告警信息字典，否则返回None。
        """
        try:
            threshold_str = os.getenv('ELECTRICITY_ALERT_THRESHOLD', '20')
            threshold = float(threshold_str)
            
            if current_balance < threshold:
                logging.warning(f"低电量告警！当前电量 {current_balance:.2f} 度，低于阈值 {threshold} 度。")
                return {
                    'is_alert': True,
                    'current_balance': current_balance,
                    'threshold': threshold
                }
            else:
                logging.info(f"当前电量 {current_balance:.2f} 度，高于阈值 {threshold} 度，无需告警。")
                return {
                    'is_alert': False,
                    'current_balance': current_balance,
                    'threshold': threshold
                }

        except (ValueError, TypeError) as e:
            logging.error(f"检查低电量告警时发生错误（无效的阈值配置?）: {e}")
            return None
