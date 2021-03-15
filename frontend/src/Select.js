import React, {Component} from 'react';

class Select extends Component {
  constructor(props) {
    super(props);
    this.state = {
      is_open: false
    };
  }

  togglePanel = () => {
    this.setState({
      is_open: !this.state.is_open
    });
  }

  toSelect = (value) => {
    this.togglePanel();
    this.props.onChange(value);
  }

  render() {
    let {is_open} = this.state;
    let {options} = this.props;
    let selected = !!options.find(item => item.selected === true) ? options.find(item => item.selected === true).name : options[0].name;

    return(
      <div className='select'>
        <div className={`custom-select-opener ${is_open ? 'is-open' : ''}`} onClick={this.togglePanel}>
          <span>{selected}</span>
        </div>
        <div className={`custom-select-panel ${is_open ? 'is-open' : ''}`}>
          {
            options.map((item, i) => {
              return(
                <div className='custom-select-option'
                        key={i}
                        onClick={() => {this.toSelect(item.value)}}
                >{item.name}</div>
              )
            })
          }
        </div>
      </div>
    )
  }
}

export default Select;