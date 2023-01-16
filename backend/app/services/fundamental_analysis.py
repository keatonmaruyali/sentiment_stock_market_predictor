import base64
from bs4 import BeautifulSoup
from copy import deepcopy
from datetime import datetime
from dateutil.parser import parse
from io import BytesIO
from matplotlib.figure import Figure
import pandas as pd
import re


class FundamentalAnalysis:
    def __init__(self):
        self.stat_types = [
            'balance',
            # 'operation',
            'income/loss',
            # 'stockholder/redeemable/interests/equity',
            'flow'
        ]

    def scrape(self, urls):
        return {
            i: self._get_table(
                table=BeautifulSoup(
                    open(n, "r", encoding='utf-8').read(),
                    "lxml"),
            )
            for i, n in enumerate(urls)
        }

    def _clean_table(self, table):
        data_table = deepcopy(table)
        data_table.rename(
            columns={data_table.columns[0]: 'index'},
            inplace=True,
        )
        basic_index = [
            i
            for i, index in enumerate(list(data_table['index']))
            if index == 'Basic'
        ]
        for i in basic_index:
            data_table["index"][i] = f'{data_table["index"][i-1]} Basic'
            data_table["index"][i+1] = f'{data_table["index"][i-1]} Diluted'

        data_table.set_index('index', inplace=True)
        good_col = [
            i
            for i in range(1, len(data_table.iloc[0]))
            if (
                (
                    (data_table.iloc[:, i].values == '').sum()/len(data_table.iloc[:, i])
                )*100 <= 40
                and any(
                    x
                    not in data_table.index.values
                    for x
                    in list(filter(None, data_table.iloc[:, i]))
                )
            )
        ]
        data_table = data_table.iloc[:, good_col]

        bad_rows = [
            n
            for n in range(len(data_table.index.values))
            if data_table.index.values[n] == ''
        ]
        good_rows = [
            n
            for n in range(1, len(data_table.index.values))
            if n not in bad_rows
        ]

        new_header_row = int(good_rows[0])-1
        new_head = [
            data_table.iloc[:new_header_row+1, i].sum()
            for i, n in enumerate(data_table.iloc[new_header_row])
        ]
        data_table.columns = new_head
        data_table.iloc[new_header_row] = ''
        data_table.drop(data_table.index[bad_rows], inplace=True)

        return data_table

    def _get_table(self, table):
        quarter_data_tables = {}
        for stattype in self.stat_types:
            patterns = stattype.split('/')

            if len(patterns) > 1:
                to_stop = False
                for pattern in patterns:
                    if not to_stop:
                        oper = table.find(
                            "p",
                            {'id': re.compile(pattern, re.IGNORECASE)},
                        )
                        if oper is not None:
                            to_stop = True
            else:
                oper = table.find(
                    "p",
                    {'id': re.compile(patterns[0], re.IGNORECASE)},
                )
            oper_statement = pd.read_html(
                str(oper.findNext('table')),
                na_values=' ',
                keep_default_na=False,
            )
            quarter_data_tables[stattype] = self._clean_table(
                oper_statement[0]
            )
        return quarter_data_tables

    def _generate_clean_statements(self, df_data):
        try:
            new_header = [
                datetime.strptime(
                    header.replace(u'\xa0', u' '),
                    '%B %d,%Y'
                ).date()
                for header in df_data.columns
            ]
            df_data.columns = new_header
        except:
            pass

        # Sort the header:
        df_data = df_data.loc[:, ~df_data.columns.duplicated()].copy()
        df_data = df_data.reindex(sorted(df_data.columns), axis=1)
        t_data_df = df_data.transpose()

        replacers = {
            ',': '',
            '—': '',
            r'\(': '-',
        }
        t_data_df.replace(replacers, regex=True, inplace=True)

        # Make the values numerical so that they can be plotted:
        for col in t_data_df.columns:
            try:
                t_data_df[col] = pd.to_numeric(t_data_df[col])
            except:
                pass

        t_data_df.fillna(0.0, inplace=True)
        return t_data_df

    def generate_all_state_figs(self, all_statements):
        all_results = {
            stype: pd.concat(
                [
                    i[k]
                    for i in all_statements.values()
                    for k in i
                    if stype == k
                ],
                axis=1,
            )
            for stype in self.stat_types
        }

        return {
            stat_type: self._statement_figures(
                all_statements=all_results,
                stat_type=stat_type,
                fig_size=len(self.stat_types),
            )
            for stat_type in self.stat_types
        }

    def _statement_figures(self, all_statements, stat_type, fig_size):
        # print(f'Statement Type: {stat_type}')
        fig_data = {}
        if stat_type == 'balance':
            balance_df = self._generate_clean_statements(
                all_statements['balance']
            )

            total_balance_stmts = [
                i
                for i, col in enumerate(balance_df, start=1)
                if 'total' in col.lower()
            ]
            total_balance_stmts.insert(0, 0)

            bstat_col = [
                list(
                    balance_df.iloc[
                        :,
                        total_balance_stmts[i]:total_balance_stmts[i+1]
                    ].columns)
                for i in range(len(total_balance_stmts)-1)
            ]

            fig = Figure(figsize=(40, 30))
            for i in range(len(bstat_col)):
                ax = fig.add_subplot(4, 2, i+1)
                ax.plot(
                    balance_df[bstat_col[i][:-1]],
                    '-o',
                    label=bstat_col[i][:-1],
                    linewidth=0.75,
                )
                ax.plot(
                    balance_df[bstat_col[i][-1]],
                    '-o',
                    label=bstat_col[i][-1],
                    linewidth=3,
                )
                ax.legend()

            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            fig_data[stat_type] = base64.b64encode(
                buf.getbuffer()
            ).decode("ascii")

        if stat_type in ['income/loss', 'flow']:
            income_loss_df = self._generate_clean_statements(
                all_statements['income/loss']
            )

            empty_col = [
                i
                for i in range(len(income_loss_df.iloc[0])-1)
                if ((
                    income_loss_df.iloc[:, i].values == 0.0
                ).sum()/len(income_loss_df.iloc[:, i])) == 1
            ]

            if 0 not in empty_col:
                empty_col.insert(0, -1)
            empty_col
            incstat_col = [
                list(
                    income_loss_df.iloc[
                        :,
                        empty_col[i]+1:empty_col[i+1]
                    ].columns
                )
                for i in range(len(empty_col)-1)
            ]
            # print(incstat_col)
            striped_ind2 = [
                parse(dtstr.replace(',', ' '), fuzzy_with_tokens=True)[0]
                for dtstr in income_loss_df.index
            ]
            income_loss_df['dates'] = striped_ind2

            income_index = {
                i : [
                    ind
                    for ind in income_loss_df.index
                    if i in ind.lower()
                ]
                for i in ['three', 'six', 'nine']
            }

            fig = Figure(figsize=(40, 50))
            count = 1
            for _, k in enumerate(['three', 'six', 'nine']):
                reduced_df = income_loss_df.loc[income_index[k]]
                ordered_red_df = reduced_df.sort_values(by=['dates'])

                for i in range(len(incstat_col)):
                    ax = fig.add_subplot(3, len(incstat_col), count)
                    ax.plot(
                        ordered_red_df.loc[:, 'dates'],
                        ordered_red_df.loc[:, incstat_col[i]].values,
                        '-o',
                        label=incstat_col[i],
                        # linewidth=0.75,
                    )
                    ax.legend()
                    # ax.set_title(incstat_col[i])
                    count += 1
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            fig_data[stat_type] = base64.b64encode(
                buf.getbuffer()
            ).decode("ascii")
        return fig_data
