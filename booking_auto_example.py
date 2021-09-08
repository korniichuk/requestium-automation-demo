#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Name: booking_auto_example
# Version: 0.1a1
# Owner: Ruslan Korniichuk

import argparse
import os
import sys
import time

import arrow
import boto3
from bs4 import BeautifulSoup
from loguru import logger
from requestium import Session

PHONE_NUMBER = '0048888888888'
DRIVER = '/usr/lib/chromium-browser/chromedriver'
TRIES = 5
DEFAULT_TIMEOUT = 15


def parse_dates(page, logger=None):
    """Get available dates from input page source."""

    result = []

    soap = BeautifulSoup(page, 'lxml')
    spans = soap.findAll('span', class_='vc-focusable')
    for span in spans:
        if 'vc-text-gray-400' not in str(span):
            if logger:
                logger.debug('Available date was found')
            label = span.get('aria-label')
            if logger:
                logger.debug(f'aria-label: {label}')
            date = arrow.get(label, 'dddd, MMMM D, YYYY')
            date = date.format('DD-MM-YYYY (dddd)')
            if logger:
                logger.debug(f'date: {date}')
            result.append(date)
            if logger:
                logger.debug(f"'{date}' date was added")
    return result


def collect_dates(
        url, headless, no_sandbox, disable_dev_shm_usage, logger=None):
    """Collect available dates from input URL."""

    result = []

    for i in range(TRIES):
        if logger:
            logger.debug(f'Try {i+1}/{TRIES}...')
        try:
            # Start session
            arguments = []
            if headless:
                arguments.append('headless')
            if no_sandbox:
                arguments.append('no-sandbox')
            if disable_dev_shm_usage:
                arguments.append('disable-dev-shm-usage')
            s = Session(webdriver_path=DRIVER,
                        browser='chrome',
                        default_timeout=DEFAULT_TIMEOUT,
                        webdriver_options={'arguments': arguments})
            if logger:
                logger.debug('Session was started')

            # Select 'Pobyt - Odbiór karty pobytu lub decyzji'
            s.driver.get(url)
            text = 'Pobyt - Odbiór karty pobytu lub decyzji'
            xpath = f"//button[text()='{text}']"
            s.driver.ensure_element_by_xpath(xpath).send_keys('\n')
            if logger:
                logger.debug("Selected 'Pobyt ...'")
            time.sleep(1)

            # Click 'Dalej'
            text = 'Dalej'
            xpath = f"//button[text()='{text}']"
            s.driver.ensure_element_by_xpath(xpath).send_keys('\n')
            if logger:
                logger.debug("Clicked 'Dalej'")
            time.sleep(1)

            # Wait for next month button
            name = 'vc-pointer-events-auto'
            try:
                next_month_button = s.driver.ensure_element_by_class_name(name)
            except BaseException as e:
                if logger:
                    logger.error("Timeout for 'next month' button readiness")
                raise e
            if logger:
                logger.debug("The 'next month' button is ready")

            # Parse first month
            page_source = s.driver.page_source
            dates = parse_dates(page_source, logger)
            if dates != [arrow.now().format('DD-MM-YYYY (dddd)')]:
                if logger:
                    logger.info('Parsed the first month')
                result.extend(dates)
                if logger:
                    logger.debug(f'result: {result}')
            else:
                if logger:
                    logger.error('Loaded incomplete page')
                raise BaseException('Loaded incomplete page')

            # Select second month
            s.driver.execute_script('arguments[0].click();', next_month_button)
            if logger:
                logger.info('Selected the second month')

            # Parse second month
            page_source = s.driver.page_source
            dates = parse_dates(page_source, logger)
            if logger:
                logger.info('Parsed the second month')
            result.extend(dates)
            if logger:
                logger.debug(f'result: {result}')
        except BaseException as e:
            if logger:
                logger.error(e)
            result = []
            time.sleep(5)
        else:
            break
        finally:
            s.driver.close()
    else:
        if logger:
            logger.error(f'Failed dates collection from {url}')
        raise BaseException(f'Failed dates collection from {url}')
    return result


def send_sms(msg, phone_number, logger=None):
    """Send SMS with Amazon SNS service."""

    if logger:
        logger.debug(f"msg: '{msg}'")
        logger.debug(f"phone_number: '{phone_number}'")
    sns = boto3.client('sns')
    try:
        sns.publish(PhoneNumber=phone_number, Message=msg)
    except BaseException as e:
        if logger:
            logger.error(e)
        raise e
    if logger:
        logger.info(f'SMS with available dates was sent to {phone_number}.')


if __name__ == '__main__':
    # Load arguments
    description = 'Check available dates at https://bezkolejki.eu/suw'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--headless', action='store_true',
                        help='runs Chrome in headless mode')
    parser.add_argument('--no-sandbox', action='store_true',
                        help='removes sandbox from Chrome')
    msg = 'writes shared memory files into /tmp instead of /dev/shm'
    parser.add_argument('--disable-dev-shm-usage', action='store_true',
                        help=msg)
    parser.add_argument('--sms', action='store_true',
                        help='enables SMS notification')
    args = parser.parse_args()
    headless = args.headless
    no_sandbox = args.no_sandbox
    disable_dev_shm_usage = args.disable_dev_shm_usage
    sms = args.sms

    # Configure logging
    fmt = '{time}\t{level}\t{module}\t{message}'
    logger.remove()
    logger.add(sys.stderr, format=fmt, level='DEBUG')  # DEBUG | INFO
    script_filename = os.path.basename(__file__)
    log_filename = os.path.splitext(script_filename)[0] + '.log'
    log_path = '/var/log/booking/{}'.format(log_filename)
    logger.add(log_path, format=fmt, level='DEBUG')  # DEBUG | INFO

    # Collect available dates from URL
    url = 'https://bezkolejki.eu/suw'
    dates = collect_dates(
            url, headless, no_sandbox, disable_dev_shm_usage, logger)
    logger.debug(f'dates: {dates}')
    dates = list(set(dates))
    logger.info(f'Available dates: {dates}')

    # Send via SMS
    if dates and sms:
        msg = '\n'.join(dates)
        send_sms(msg, PHONE_NUMBER, logger)

    logger.info('Done!')
